from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import RegistroForm
from .models import Ingrediente
from django.shortcuts import redirect, get_object_or_404
from .models import KitPersonalizado, KitIngrediente
from .models import Carrito, CarritoItem
from django.db.models import Q
import stripe
from django.conf import settings
from .models import Pedido, PedidoKit
from django.contrib import messages

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inicio')
    else:
        form = RegistroForm()
    return render(request, 'tienda/registro.html', {'form': form})

def inicio(request):
    return render(request, 'tienda/inicio.html')

@login_required
def perfil(request):
    return render(request, 'tienda/perfil.html')

# Vista pública: cualquier usuario puede ver los ingredientes
def listar_ingredientes(request):
    ingredientes = Ingrediente.objects.all()
    return render(request, 'tienda/ingredientes.html', {'ingredientes': ingredientes})

@login_required
def crear_kit(request):
    if hasattr(request.user, 'perfil') and request.user.perfil.es_repartidor:
        return redirect('pedidos_pendientes')
    if request.method == 'POST':
        kit = KitPersonalizado.objects.create(
            nombre="Temporal",
            usuario=request.user
        )
        ingredientes_ids = request.POST.getlist('ingredientes')
        for ing_id in ingredientes_ids:
            cantidad = request.POST.get(f'cantidad_{ing_id}', 1)
            if int(cantidad) > 0:
                ingrediente = get_object_or_404(Ingrediente, id=ing_id)
                KitIngrediente.objects.create(
                    kit=kit,
                    ingrediente=ingrediente,
                    cantidad=int(cantidad)
                )
        kit.nombre = kit.nombre_sugerido()
        kit.save()
        return redirect('mis_kits')

    ingredientes = Ingrediente.objects.all().order_by('categoria')
    return render(request, 'tienda/crear_kit.html', {'ingredientes': ingredientes})

@login_required
def mis_kits(request):
    if hasattr(request.user, 'perfil') and request.user.perfil.es_repartidor:
        return redirect('pedidos_pendientes')
    kits = KitPersonalizado.objects.filter(usuario=request.user).order_by('-fecha_creacion')
    return render(request, 'tienda/mis_kits.html', {'kits': kits})

@login_required
def eliminar_kit(request, kit_id):
    if hasattr(request.user, 'perfil') and request.user.perfil.es_repartidor:
        return redirect('pedidos_pendientes')
    kit = get_object_or_404(KitPersonalizado, id=kit_id, usuario=request.user)
    if request.method == 'POST':
        kit.delete()
        return redirect('mis_kits')
    return redirect('mis_kits')

@login_required
def agregar_al_carrito(request, kit_id):
    if hasattr(request.user, 'perfil') and request.user.perfil.es_repartidor:
        return redirect('pedidos_pendientes')
    kit = get_object_or_404(
        KitPersonalizado.objects.filter(
            Q(usuario=request.user) | Q(usuario__isnull=True)
        ),
        id=kit_id
    )
    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
    carrito_item, created = CarritoItem.objects.get_or_create(carrito=carrito, kit=kit)
    if not created:
        carrito_item.cantidad += 1
        carrito_item.save()
    return redirect('ver_carrito')

@login_required
def ver_carrito(request):
    if hasattr(request.user, 'perfil') and request.user.perfil.es_repartidor:
        return redirect('pedidos_pendientes')
    carrito, created = Carrito.objects.get_or_create(usuario=request.user)
    items = carrito.items.all()
    total = carrito.total_carrito()
    return render(request, 'tienda/carrito.html', {'items': items, 'total': total})

@login_required
def eliminar_del_carrito(request, item_id):
    if hasattr(request.user, 'perfil') and request.user.perfil.es_repartidor:
        return redirect('pedidos_pendientes')
    item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=request.user)
    item.delete()
    return redirect('ver_carrito')

@login_required
def actualizar_cantidad_carrito(request, item_id):
    if hasattr(request.user, 'perfil') and request.user.perfil.es_repartidor:
        return redirect('pedidos_pendientes')
    if request.method == 'POST':
        item = get_object_or_404(CarritoItem, id=item_id, carrito__usuario=request.user)
        nueva_cantidad = int(request.POST.get('cantidad', 1))
        if nueva_cantidad > 0:
            item.cantidad = nueva_cantidad
            item.save()
        else:
            item.delete()
    return redirect('ver_carrito')

@login_required
def detalle_kit(request, kit_id):
    if hasattr(request.user, 'perfil') and request.user.perfil.es_repartidor:
        return redirect('pedidos_pendientes')
    kit = get_object_or_404(
        KitPersonalizado.objects.filter(
            Q(usuario=request.user) | Q(usuario__isnull=True)
        ),
        id=kit_id
    )
    atributos = kit.calcular_atributos()
    atributos['energia_pct'] = atributos['energia'] * 10
    atributos['dulzor_pct'] = atributos['dulzor'] * 10
    atributos['intensidad_pct'] = atributos['intensidad'] * 10
    nombre_auto = kit.nombre_sugerido()
    return render(request, 'tienda/detalle_kit.html', {
        'kit': kit,
        'atributos': atributos,
        'nombre_auto': nombre_auto
    })

@login_required
def barista_virtual(request):
    recomendaciones = []
    if request.method == 'POST':
        energia_deseada = int(request.POST.get('energia', 5))
        dulzor_deseado = int(request.POST.get('dulzor', 5))
        intensidad_deseada = int(request.POST.get('intensidad', 5))

        # Obtener todos los kits (propios + predefinidos)
        kits_a_evaluar = KitPersonalizado.objects.filter(
            Q(usuario=request.user) | Q(usuario__isnull=True)
        )

        lista_con_diferencia = []
        for kit in kits_a_evaluar:
            attrs = kit.calcular_atributos()
            # Calcular diferencia absoluta total (máximo 30 puntos)
            diff = abs(attrs['energia'] - energia_deseada) + \
                   abs(attrs['dulzor'] - dulzor_deseado) + \
                   abs(attrs['intensidad'] - intensidad_deseada)
            # Solo considerar si la diferencia es <= 8 (puedes ajustar este umbral)
            if diff <= 8:
                lista_con_diferencia.append((kit, diff))

        # Ordenar de menor a mayor diferencia
        lista_con_diferencia.sort(key=lambda x: x[1])
        # Tomar solo los 3 primeros (los más cercanos)
        recomendaciones = [kit for kit, diff in lista_con_diferencia[:3]]

        if not recomendaciones:
            messages.info(request, "No encontramos kits muy cercanos a tus gustos. ¡Prueba crear el tuyo propio!")

    return render(request, 'tienda/barista.html', {'recomendaciones': recomendaciones})

@login_required
def checkout(request):
    if hasattr(request.user, 'perfil') and request.user.perfil.es_repartidor:
        return redirect('pedidos_pendientes')
    carrito = Carrito.objects.get(usuario=request.user)
    items = carrito.items.all()
    if not items:
        return redirect('ver_carrito')

    total = carrito.total_carrito()

    if request.method == 'POST':
        pedido = Pedido.objects.create(
            usuario=request.user,
            total=total,
            estado='PENDIENTE',
            direccion_envio=request.user.perfil.direccion if hasattr(request.user, 'perfil') else ''
        )
        for item in items:
            PedidoKit.objects.create(
                pedido=pedido,
                kit=item.kit,
                cantidad=item.cantidad,
                precio_unitario=item.kit.calcular_total()
            )
        items.delete()
        return redirect('mis_pedidos')

    context = {
        'items': items,
        'total': total,
        'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'tienda/checkout.html', context)

@login_required
def mis_pedidos(request):
    if hasattr(request.user, 'perfil') and request.user.perfil.es_repartidor:
        return redirect('pedidos_pendientes')
    pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha')
    return render(request, 'tienda/mis_pedidos.html', {'pedidos': pedidos})

# Decorador para vistas de repartidor
def repartidor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'perfil') or not request.user.perfil.es_repartidor:
            return redirect('inicio')
        return view_func(request, *args, **kwargs)
    return wrapper

@repartidor_required
def pedidos_pendientes(request):
    pedidos = Pedido.objects.filter(estado='PENDIENTE').order_by('-fecha')
    return render(request, 'tienda/pedidos_pendientes.html', {'pedidos': pedidos})

@repartidor_required
def pedidos_completados(request):
    pedidos = Pedido.objects.filter(estado='ENTREGADO').order_by('-fecha')
    return render(request, 'tienda/pedidos_completados.html', {'pedidos': pedidos})

@repartidor_required
def completar_pedido(request, pedido_id):
    if request.method == 'POST':
        pedido = get_object_or_404(Pedido, id=pedido_id, estado='PENDIENTE')
        pedido.estado = 'ENTREGADO'
        pedido.save()
    return redirect('pedidos_pendientes')