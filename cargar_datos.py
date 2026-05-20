import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from tienda.models import Ingrediente, KitPersonalizado, KitIngrediente
from django.contrib.auth.models import User

# ============================================================
# 1. Ingredientes (según tu tabla, con acentos correctos)
# ============================================================
ingredientes_data = [
    {"pk": 1, "nombre": "Vaso transparente", "categoria": "VASO", "precio": 25.00, "nivel_energia": 0, "nivel_dulzor": 0, "nivel_intensidad": 0},
    {"pk": 2, "nombre": "Café Espresso", "categoria": "BASE", "precio": 35.00, "nivel_energia": 8, "nivel_dulzor": 2, "nivel_intensidad": 9},
    {"pk": 3, "nombre": "Leche de Almendra", "categoria": "LECHE", "precio": 15.00, "nivel_energia": 2, "nivel_dulzor": 1, "nivel_intensidad": 0},
    {"pk": 4, "nombre": "Sirope de Vainilla", "categoria": "SABOR", "precio": 10.00, "nivel_energia": 4, "nivel_dulzor": 10, "nivel_intensidad": 3},
    {"pk": 5, "nombre": "Stevia", "categoria": "ENDULZANTE", "precio": 5.00, "nivel_energia": 2, "nivel_dulzor": 8, "nivel_intensidad": 1},
    {"pk": 6, "nombre": "Chispas de Chocolate", "categoria": "TOPPING", "precio": 8.00, "nivel_energia": 4, "nivel_dulzor": 7, "nivel_intensidad": 1},
    {"pk": 7, "nombre": "Matcha", "categoria": "BASE", "precio": 40.00, "nivel_energia": 4, "nivel_dulzor": 2, "nivel_intensidad": 5},
    {"pk": 8, "nombre": "Leche de Avena", "categoria": "LECHE", "precio": 15.00, "nivel_energia": 4, "nivel_dulzor": 4, "nivel_intensidad": 2},
    {"pk": 9, "nombre": "Canela en polvo", "categoria": "SABOR", "precio": 7.00, "nivel_energia": 1, "nivel_dulzor": 4, "nivel_intensidad": 4},
    {"pk": 10, "nombre": "Azúcar Mascabado", "categoria": "ENDULZANTE", "precio": 4.00, "nivel_energia": 2, "nivel_dulzor": 9, "nivel_intensidad": 2},
]

print("🚀 Insertando ingredientes...")
for ing_data in ingredientes_data:
    obj, created = Ingrediente.objects.get_or_create(
        pk=ing_data["pk"],
        defaults={
            "nombre": ing_data["nombre"],
            "categoria": ing_data["categoria"],
            "precio": ing_data["precio"],
            "nivel_energia": ing_data["nivel_energia"],
            "nivel_dulzor": ing_data["nivel_dulzor"],
            "nivel_intensidad": ing_data["nivel_intensidad"],
        }
    )
    if created:
        print(f"✅ Creado: {obj.nombre}")
    else:
        print(f"⚠️ Ya existía: {obj.nombre}")

# ============================================================
# 2. Kits predefinidos (usuario = None)
# ============================================================
kits_data = [
    {"pk": 12, "nombre": "Clásico Espresso"},
    {"pk": 13, "nombre": "Vainilla Dream"},
    {"pk": 14, "nombre": "Matcha Latte"},
    {"pk": 15, "nombre": "Energía Oscura"},
    {"pk": 16, "nombre": "Dulce Tentación"},
]

print("\n📦 Insertando kits predefinidos...")
for kit_data in kits_data:
    obj, created = KitPersonalizado.objects.get_or_create(
        pk=kit_data["pk"],
        defaults={
            "nombre": kit_data["nombre"],
            "usuario": None,
        }
    )
    if created:
        print(f"✅ Creado: {obj.nombre}")
    else:
        print(f"⚠️ Ya existía: {obj.nombre}")

# ============================================================
# 3. Relaciones KitIngrediente (usando los ID reales)
# ============================================================
# Mapeo: (kit_pk, ingrediente_pk, cantidad)
kitingredientes_data = [
    (12, 2, 1), (12, 3, 1), (12, 10, 1), (12, 6, 1),  # Clásico Espresso
    (13, 2, 1), (13, 8, 1), (13, 4, 1), (13, 5, 1),  # Vainilla Dream
    (14, 7, 1), (14, 3, 1), (14, 9, 1), (14, 5, 1),  # Matcha Latte
    (15, 2, 2), (15, 3, 1), (15, 9, 1),              # Energía Oscura
    (16, 2, 1), (16, 8, 1), (16, 4, 1), (16, 10, 1), (16, 6, 1),  # Dulce Tentación
]

print("\n🔗 Insertando relaciones KitIngrediente...")
for kit_pk, ing_pk, cantidad in kitingredientes_data:
    try:
        kit = KitPersonalizado.objects.get(pk=kit_pk)
        ing = Ingrediente.objects.get(pk=ing_pk)
        obj, created = KitIngrediente.objects.get_or_create(
            kit=kit,
            ingrediente=ing,
            defaults={"cantidad": cantidad}
        )
        if created:
            print(f"✅ {kit.nombre} + {ing.nombre} (x{cantidad})")
        else:
            # Si ya existe pero con cantidad diferente, actualizar
            if obj.cantidad != cantidad:
                obj.cantidad = cantidad
                obj.save()
                print(f"🔄 Actualizado {kit.nombre} + {ing.nombre} a x{cantidad}")
            else:
                print(f"⚠️ Ya existía: {kit.nombre} + {ing.nombre}")
    except Exception as e:
        print(f"❌ Error con kit {kit_pk} / ing {ing_pk}: {e}")

print("\n🎉 ¡Datos cargados exitosamente!")