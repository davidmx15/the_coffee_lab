import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tienda.models import Ingrediente, KitPersonalizado, KitIngrediente

def crear_kit(nombre, ingredientes_con_cantidad):
    """
    ingredientes_con_cantidad: lista de tuplas (nombre_ingrediente, cantidad)
    """
    # Verificar si ya existe un kit con ese nombre (evita duplicados)
    if KitPersonalizado.objects.filter(nombre=nombre, usuario__isnull=True).exists():
        print(f"⚠️ El kit '{nombre}' ya existe. No se creará duplicado.")
        return None
    
    # Crear el kit (sin usuario = predefinido)
    kit = KitPersonalizado.objects.create(nombre=nombre, usuario=None)
    
    # Agregar los ingredientes con sus cantidades
    for nombre_ing, cantidad in ingredientes_con_cantidad:
        try:
            ingrediente = Ingrediente.objects.get(nombre=nombre_ing)
            KitIngrediente.objects.create(
                kit=kit,
                ingrediente=ingrediente,
                cantidad=cantidad
            )
        except Ingrediente.DoesNotExist:
            print(f"❌ Error: No se encontró el ingrediente '{nombre_ing}'. Kit '{nombre}' incompleto.")
            kit.delete()  # eliminar kit parcial
            return None
    
    # Calcular atributos (solo para mostrar en consola)
    atributos = kit.calcular_atributos()
    print(f"✅ Kit '{nombre}' creado → ⚡{atributos['energia']} 🍬{atributos['dulzor']} 🔥{atributos['intensidad']}")
    return kit

def main():
    print("🚀 Insertando kits predefinidos...\n")
    
    kits_data = [
        ("Clásico Espresso", [
            ("Café Espresso", 1),
            ("Leche de Almendra", 1),
            ("Azúcar Mascabado", 1),
            ("Chispas de Chocolate", 1),
        ]),
        ("Vainilla Dream", [
            ("Café Espresso", 1),
            ("Leche de Avena", 1),
            ("Sirope de Vainilla", 1),
            ("Stevia", 1),
        ]),
        ("Matcha Latte", [
            ("Matcha", 1),
            ("Leche de Almendra", 1),
            ("Canela en polvo", 1),
            ("Stevia", 1),
        ]),
        ("Energía Oscura", [
            ("Café Espresso", 2),   # doble dosis
            ("Leche de Almendra", 1),
            ("Canela en polvo", 1),
        ]),
        ("Dulce Tentación", [
            ("Café Espresso", 1),
            ("Leche de Avena", 1),
            ("Sirope de Vainilla", 1),
            ("Azúcar Mascabado", 1),
            ("Chispas de Chocolate", 1),
        ]),
    ]
    
    for nombre, ingredientes in kits_data:
        crear_kit(nombre, ingredientes)
    
    print("\n🎉 Proceso completado.")

if __name__ == "__main__":
    main()