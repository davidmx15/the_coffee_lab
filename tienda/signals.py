from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import PerfilUsuario, Carrito
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(usuario=instance)

def crear_perfil_y_carrito(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(usuario=instance)
        Carrito.objects.create(usuario=instance)