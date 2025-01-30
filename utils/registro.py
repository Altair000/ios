# Módulos de terceros
import threading
import uuid
import hashlib
from datetime import datetime
# Módulos locales
from configs.bot_config import bot
from configs.registro import *

# Variable global para almacenar vouchers
vouchers_db = {}

def eliminar_datos_temporales(user_id):
    """Elimina los datos temporales de un usuario tras el timeout."""
    if user_id in usuarios_en_proceso:
        usuarios_en_proceso.pop(user_id, None)
        bot.send_message(user_id, "⏳ Tiempo agotado. Por favor, reinicia el proceso de creación de cuenta con /cuenta_ayuda.")

def iniciar_timeout(user_id):
    """Inicia un temporizador de 10 minutos para eliminar los datos temporales."""
    if user_id in timers:
        timers[user_id].cancel()
    timer = threading.Timer(600, eliminar_datos_temporales, args=(user_id,))
    timers[user_id] = timer
    timer.start()

def cancelar_timeout(user_id):
    """Cancela el timeout para un usuario."""
    if user_id in timers:
        timers[user_id].cancel()
        timers.pop(user_id, None)

def validar_voucher(voucher_code, user_id):
    """Valida un voucher y marca su estado como usado."""
    # Verificar si existe en la base de datos
    if voucher_code not in vouchers_db:
        return False, "El voucher es inválido."

    voucher = vouchers_db[voucher_code]

    # Verificar si está vinculado al usuario correcto
    if voucher["user_id"] != user_id:
        return False, "El voucher no está vinculado a tu cuenta."

    # Verificar si ya fue usado
    if voucher["status"] != "valid":
        return False, "El voucher ya ha sido utilizado."

    # Marcar el voucher como usado
    vouchers_db[voucher_code]["status"] = "used"
    return True, "El voucher es válido."

def generar_voucher(user_id):
    """Genera un voucher único vinculado a un usuario."""
    # Datos básicos del voucher
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    unique_id = f"{user_id}-{timestamp}-{uuid.uuid4()}"

    # Hash seguro para el voucher
    voucher_code = hashlib.sha256(unique_id.encode()).hexdigest()[:10].upper()

    # Almacenar en la base de datos
    vouchers_db[voucher_code] = {
        "user_id": user_id,
        "timestamp": timestamp,
        "status": "valid"
    }

    return voucher_code