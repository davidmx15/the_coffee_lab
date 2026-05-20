from django.contrib import admin
from .models import Ingrediente, KitPersonalizado, KitIngrediente, Pedido, PedidoKit, PerfilUsuario

class KitIngredienteInline(admin.TabularInline):
    model = KitIngrediente
    extra = 1

@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock')
    list_filter = ('categoria',)
    search_fields = ('nombre',)

@admin.register(KitPersonalizado)
class KitPersonalizadoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'usuario', 'fecha_creacion')
    inlines = [KitIngredienteInline]

@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha', 'estado', 'total')

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'telefono', 'direccion', 'es_repartidor')
    list_filter = ('es_repartidor',)

admin.site.register(KitIngrediente)
admin.site.register(PedidoKit)