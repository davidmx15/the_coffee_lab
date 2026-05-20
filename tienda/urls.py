from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Autenticación
    path('registro/', views.registro, name='registro'),
    path('login/', auth_views.LoginView.as_view(template_name='tienda/login.html', next_page='inicio'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Páginas principales
    path('', views.inicio, name='inicio'),
    path('perfil/', views.perfil, name='perfil'),
    path('ingredientes/', views.listar_ingredientes, name='ingredientes'),
    path('crear-kit/', views.crear_kit, name='crear_kit'),
    path('mis-kits/', views.mis_kits, name='mis_kits'),
    path('eliminar-kit/<int:kit_id>/', views.eliminar_kit, name='eliminar_kit'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('agregar-carrito/<int:kit_id>/', views.agregar_al_carrito, name='agregar_al_carrito'),
    path('eliminar-item-carrito/<int:item_id>/', views.eliminar_del_carrito, name='eliminar_item_carrito'),
    path('actualizar-cantidad/<int:item_id>/', views.actualizar_cantidad_carrito, name='actualizar_cantidad'),
    path('kit/<int:kit_id>/', views.detalle_kit, name='detalle_kit'),
    path('barista/', views.barista_virtual, name='barista'),
    path('checkout/', views.checkout, name='checkout'),
    path('mis-pedidos/', views.mis_pedidos, name='mis_pedidos'),
    path('repartidor/pendientes/', views.pedidos_pendientes, name='pedidos_pendientes'),
    path('repartidor/completados/', views.pedidos_completados, name='pedidos_completados'),
    path('repartidor/completar/<int:pedido_id>/', views.completar_pedido, name='completar_pedido'),
]