from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# ------------------------------------------------------------
# 1. Modelo Ingrediente (cada sobre o componente)
# ------------------------------------------------------------
class Ingrediente(models.Model):
    CATEGORIAS = [
        ('BASE', 'Base (Café/Té/Chocolate)'),
        ('LECHE', 'Leche o Creamer'),
        ('SABOR', 'Saborizante/Jarabe'),
        ('ENDULZANTE', 'Endulzante'),
        ('TOPPING', 'Topping'),
        ('VASO', 'Vaso'),
    ]

    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=20, choices=CATEGORIAS)
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=6, decimal_places=2)
    stock = models.IntegerField(default=0)
    imagen = models.ImageField(upload_to='ingredientes/', blank=True, null=True)

    # Atributos para gamificación (escala 0-10)
    nivel_energia = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    nivel_dulzor = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])
    nivel_intensidad = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(10)])

    def __str__(self):
        return f"{self.nombre} (${self.precio})"


# ------------------------------------------------------------
# 2. Modelo KitPersonalizado (receta creada por el usuario)
# ------------------------------------------------------------
class KitPersonalizado(models.Model):
    nombre = models.CharField(max_length=100, default="Mi Kit")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ingredientes = models.ManyToManyField(Ingrediente, through='KitIngrediente')

    def calcular_total(self):
        total = 0
        for item in self.kitingrediente_set.all():
            total += item.ingrediente.precio * item.cantidad
        return total

    def calcular_atributos(self):
        energia = dulzor = intensidad = 0.0
        peso_total = 0

        for item in self.kitingrediente_set.all():
            ing = item.ingrediente
            cantidad = item.cantidad

            # Excluir el vaso (categoría 'VASO')
            if ing.categoria == 'VASO':
                continue

            # Definir pesos por categoría
            if ing.categoria == 'BASE':
                peso = 3
            elif ing.categoria == 'LECHE':
                peso = 2
            elif ing.categoria == 'SABOR':
                peso = 3
            elif ing.categoria == 'ENDULZANTE':
                peso = 5
            elif ing.categoria == 'TOPPING':
                peso = 4
            else:
                peso = 1

            energia += ing.nivel_energia * cantidad * peso
            dulzor += ing.nivel_dulzor * cantidad * peso
            intensidad += ing.nivel_intensidad * cantidad * peso
            peso_total += cantidad * peso

        if peso_total > 0:
            energia = round(energia / peso_total)
            dulzor = round(dulzor / peso_total)
            intensidad = round(intensidad / peso_total)

            # Asegurar que no excedan 10
            energia = min(10, max(0, energia))
            dulzor = min(10, max(0, dulzor))
            intensidad = min(10, max(0, intensidad))
        else:
            energia = dulzor = intensidad = 0

        return {'energia': energia, 'dulzor': dulzor, 'intensidad': intensidad}

    def __str__(self):
        return f"{self.nombre} (de {self.usuario.username if self.usuario else 'Anónimo'})"
    
    def nombre_sugerido(self):
        atributos = self.calcular_atributos()
        energia = atributos['energia']
        dulzor = atributos['dulzor']
        intensidad = atributos['intensidad']
        if energia >= 7 and intensidad >= 7:
            return "Explosión de Sabor"
        elif dulzor >= 7 and intensidad <= 3:
            return "Dulce Tentación"
        elif energia <= 3 and dulzor <= 3:
            return "Clásico Suave"
        elif intensidad >= 7 and dulzor <= 3:
            return "Intenso y Audaz"
        else:
            return "Creación Personalizada"
        
# ------------------------------------------------------------
# 3. Tabla intermedia para cantidad de ingredientes en un kit
# ------------------------------------------------------------
class KitIngrediente(models.Model):
    kit = models.ForeignKey(KitPersonalizado, on_delete=models.CASCADE)
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)

    class Meta:
        unique_together = ['kit', 'ingrediente']


# ------------------------------------------------------------
# 4. Pedido
# ------------------------------------------------------------
class Pedido(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('PREPARANDO', 'Preparando kit'),
        ('ENVIADO', 'Enviado'),
        ('ENTREGADO', 'Entregado'),
        ('CANCELADO', 'Cancelado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')
    total = models.DecimalField(max_digits=8, decimal_places=2)
    direccion_envio = models.TextField(blank=True)

    def __str__(self):
        return f"Pedido #{self.id} - {self.usuario.username}"


# ------------------------------------------------------------
# 5. Relación Pedido - Kit (con cantidad)
# ------------------------------------------------------------
class PedidoKit(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    kit = models.ForeignKey(KitPersonalizado, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=6, decimal_places=2)


# ------------------------------------------------------------
# 6. Perfil de usuario (datos adicionales)
# ------------------------------------------------------------
class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    es_repartidor = models.BooleanField(default=False)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"
    
class Carrito(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='carrito')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Carrito de {self.usuario.username}"

    def total_carrito(self):
        return sum(item.subtotal() for item in self.items.all())

class CarritoItem(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    kit = models.ForeignKey(KitPersonalizado, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.kit.calcular_total() * self.cantidad

    def __str__(self):
        return f"{self.cantidad} x {self.kit.nombre}"
