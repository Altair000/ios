# Módulos locales
from configs.twilios import *

def generar_numero_y_configurar(personal_number):
    """Genera un número de Twilio y configura el reenvío de SMS."""
    try:
        # Buscar un número local disponible
        number = client.available_phone_numbers('US').local.list(limit=1)[0]
        print(number.phone_number)
        # Comprar el número
        purchased_number = client.incoming_phone_numbers.create(phone_number=number.phone_number)

        # Configurar el reenvío automático de mensajes al número personal
        purchased_number.update(
            sms_url=f"https://twimlets.com/forward?PhoneNumber={personal_number}",
            sms_method="POST"
        )

        return purchased_number.phone_number
    except Exception as e:
        print(f"Error al generar número o configurar reenvío: {e}")
        return None