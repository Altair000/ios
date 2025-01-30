# Módulos de python
import os
from datetime import datetime

# Módulos de terceros
import telebot
from flask import Flask, request
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Módulos locales
from configs.bot_config import bot, ADMIN, TOKEN
from configs.registro import *
from utils.db import obtener_datos_usuario, insertar_usuario
from utils.registro import iniciar_timeout, cancelar_timeout, validar_voucher, generar_voucher
from utils.crear_apple_id import iniciar_en_hilo

# Instancia de Flask
app = Flask(__name__)

# Variables globales
WEBHOOK_URL = f"https://{os.getenv('KOYEB_APP_NAME')}.koyeb.app/{TOKEN}" # Establecer webhook automáticamente

@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    teclado_inicio = InlineKeyboardMarkup()
    cuenta_btn = InlineKeyboardButton('Cuenta', callback_data='cuenta')
    teclado_inicio.add(cuenta_btn)
    if chat_id == ADMIN:
        teclado_inicio.add(InlineKeyboardButton('Admin', callback_data='admin'))
    bot.send_message(chat_id, "Hola usuario, este es un bot para crear cuentas apple id desarrollado por el programador Raydiel Espinosa. El bot aun se encuentra en su version beta por lo cual podria encontrar errores o ausencia de funciones que en un futuro se solucionaran y agregaran respectivamente. Para conocer mas utilice el comando /help.", reply_markup=teclado_inicio)

@bot.message_handler(commands=['help'])
def ayuda(message):
    chat_id = message.chat.id
    mensaje_ayuda = f"""
    Para Pepe uno desde pepe dos
    """
    bot.send_message(chat_id, mensaje_ayuda)

@bot.message_handler(commands=['comprar'])
def buy(message):
    chat_id = message.chat.id
    mensaje_compra = f"""
    Tarjeta
    """

@bot.message_handler(commands=['gen_code'])
def gen_code(msg):
    chat_id = msg.chat.id
    if chat_id != ADMIN:
        bot.send_message(chat_id, "Usted no es administrador, no puede utilizar este tipo de comandos.")
        return
    # Dividir el mensaje para obtener los argumentos
    args = msg.text.split()

    # Verificar si el usuario proporcionó el ID
    if len(args) < 2:
        bot.reply_to(msg, "⚠️ Debes proporcionar un user_id. Uso correcto:\n`/comando <user_id>`", parse_mode="Markdown")
        return

    elif len(args) > 2:
        bot.reply_to(msg, "⚠️ No puedes proporcionar más de un user id. Uso correcto:\n`/comando <user_id>`", parse_mode="Markdown")
        return

    # Obtener el user_id del argumento
    user_id = args[1]

    # Validar si el user_id es numérico
    if not user_id.isdigit():
        bot.reply_to(msg, "⚠️ El user_id debe ser un número válido.")
        return

    # Convertir el user_id a entero
    user_id = int(user_id)
    if not obtener_datos_usuario(user_id):
        bot.reply_to(msg, "⚠️ El user_id no existe en la base de datos del sistema.")
        return

    voucher = generar_voucher(user_id)
    if voucher:
        bot.send_message(chat_id, f"Se ha generado satisfactoriamente el voucher para el usuario con <strong>chat_id: {user_id}</strong>", parse_mode='HTML')
        bot.send_message(user_id, f"Token recibido de la administración. Felicidades por su compra. <strong>Voucher: {voucher}</strong>", parse_mode='HTML')
    else:
        bot.send_message(chat_id, "Ha ocurrido un error al crear el voucher, inténtelo de nuevo.")

@bot.callback_query_handler(func=lambda call: call.data == 'admin')
def admin(call):
    chat_id = call.message.chat.id
    ayuda_admin = f"""
    <strong>Comandos de administración</strong>
    <strong>- /gen_code : Este comando se utiliza para generar los vouchers de usuarios. /gen_code [user_id]</strong>.
    """
    bot.send_message(chat_id, ayuda_admin, parse_mode='HTML')

@bot.callback_query_handler(func=lambda call: call.data == 'cuenta')
def cuenta(call):
    chat_id = call.message.chat.id
    if obtener_datos_usuario(chat_id):
        datos = obtener_datos_usuario(chat_id)

        teclado_cuenta = InlineKeyboardMarkup()
        apple_id_btn = InlineKeyboardButton('Apple ID', callback_data='apple_id')
        teclado_cuenta.add(apple_id_btn)

        from configs.twilios import numero_twilio
        mensaje = f"""
        📃<strong>Datos de usuario</strong>📃
        Telegram ID: {chat_id}
        Nombre: {datos[0]} {datos[1]}
        Contraseña: {datos[2]}
        Correo: {datos[3]}
        Cumpleaños: {datos[4]}
        Teléfono: {datos[5]}
        Teléfono contratado: {numero_twilio}
        """
        bot.send_message(chat_id, mensaje, parse_mode="HTML", reply_markup=teclado_cuenta)
    else:
        teclado_registro = InlineKeyboardMarkup()
        registro_btn = InlineKeyboardButton('Registrarse', callback_data='registrarse')
        teclado_registro.add(registro_btn)
        bot.send_message(chat_id, f"No existe el usuario con id: {chat_id} en la base de datos, proceda a registrarse.", reply_markup=teclado_registro)

@bot.callback_query_handler(func=lambda call: call.data == 'registrarse')
def registrar_usuario(call):
    telegram_id = call.message.chat.id
    usuarios_en_proceso[telegram_id] = {'id_telegram': telegram_id}
    msg = bot.send_message(telegram_id, "Por favor, introduce tu nombre:")
    bot.register_next_step_handler(msg, obtener_nombre)
    iniciar_timeout(telegram_id)

# Función para recoger el nombre
def obtener_nombre(message):
    telegram_id = message.chat.id
    nombre = message.text.strip()
    iniciar_timeout(telegram_id)
    if nombre.isalpha():  # Valida que el nombre solo contenga letras
        usuarios_en_proceso[telegram_id]['nombre'] = nombre
        bot.send_message(telegram_id, "Introduce tu apellido:")
        bot.register_next_step_handler(message, obtener_apellido)
    else:
        bot.send_message(telegram_id, "El nombre debe contener solo letras. Inténtalo de nuevo.")
        bot.register_next_step_handler(message, obtener_nombre)

# Función para recoger el apellido
def obtener_apellido(message):
    telegram_id = message.chat.id
    apellido = message.text.strip()
    iniciar_timeout(telegram_id)
    if apellido.isalpha():
        usuarios_en_proceso[telegram_id]['apellido'] = apellido
        bot.send_message(telegram_id, "Introduce tu contraseña:")
        bot.register_next_step_handler(message, obtener_contrasena)
    else:
        bot.send_message(telegram_id, "El apellido debe contener solo letras. Inténtalo de nuevo.")
        bot.register_next_step_handler(message, obtener_apellido)

# Función para recoger la contraseña
def obtener_contrasena(message):
    telegram_id = message.chat.id
    contrasena = message.text.strip()
    iniciar_timeout(telegram_id)
    if len(contrasena) >= 6:  # Valida que la contraseña tenga al menos 6 caracteres
        usuarios_en_proceso[telegram_id]['contrasena'] = contrasena
        bot.send_message(telegram_id, "Introduce tu correo electrónico:")
        bot.register_next_step_handler(message, obtener_correo)
    else:
        bot.send_message(telegram_id, "La contraseña debe tener al menos 6 caracteres. Inténtalo de nuevo.")
        bot.register_next_step_handler(message, obtener_contrasena)

# Función para recoger el correo electrónico
def obtener_correo(message):
    telegram_id = message.chat.id
    correo = message.text.strip()
    iniciar_timeout(telegram_id)
    if '@' in correo and '.' in correo:  # Validación básica de correo electrónico
        usuarios_en_proceso[telegram_id]['correo'] = correo
        bot.send_message(telegram_id, "Introduce tu fecha de nacimiento (dd/mm/yyyy):")
        bot.register_next_step_handler(message, obtener_fecha_nacimiento)
    else:
        bot.send_message(telegram_id, "Correo inválido. Inténtalo de nuevo.")
        bot.register_next_step_handler(message, obtener_correo)

# Función para recoger la fecha de nacimiento
def obtener_fecha_nacimiento(message):
    telegram_id = message.chat.id
    fecha_nacimiento = message.text.strip()
    iniciar_timeout(telegram_id)
    try:
        fecha = datetime.strptime(fecha_nacimiento, '%d/%m/%Y')
        usuarios_en_proceso[telegram_id]['fecha_nacimiento'] = fecha.strftime('%d/%m/%Y')
        bot.send_message(telegram_id, "Introduce tu teléfono personal (incluye el prefijo de país, ej: +5354143977):")
        bot.register_next_step_handler(message, obtener_telefono)
    except ValueError:
        bot.send_message(telegram_id, "Fecha inválida. Usa el formato dd/mm/yyyy. Inténtalo de nuevo.")
        bot.register_next_step_handler(message, obtener_fecha_nacimiento)

# Función para recoger el teléfono personal
def obtener_telefono(message):
    telegram_id = message.chat.id
    telefono = message.text.strip()
    iniciar_timeout(telegram_id)
    if telefono.startswith('+') and telefono[1:].isdigit():
        usuarios_en_proceso[telegram_id]['telefono_personal'] = telefono
        insertar_usuario(usuarios_en_proceso[telegram_id])
        bot.send_message(telegram_id, "Registro completado con éxito. Gracias!")
        cancelar_timeout(telegram_id)
        del usuarios_en_proceso[telegram_id]  # Limpia los datos temporales
    else:
        bot.send_message(telegram_id, "Teléfono inválido. Asegúrate de incluir el prefijo de país (ej: +5312345678).")
        bot.register_next_step_handler(message, obtener_telefono)

@bot.callback_query_handler(func=lambda call: call.data == 'apple_id')
def sign_up(call):
    chat_id = call.message.chat.id
    msg = bot.send_message(
        chat_id,
        "Por favor introduzca su código voucher correspondiente para activar esta función. En caso de que no posea uno, utilice el comando /comprar para obtener ayuda sobre la compra."
    )
    bot.register_next_step_handler(msg, procesar_voucher)

def procesar_voucher(message):
    chat_id = message.chat.id
    voucher_code = message.text.strip()  # Captura el texto ingresado por el usuario
    resultado, mensaje = validar_voucher(voucher_code, chat_id)  # Llama a la función de validación

    if resultado:
        msg = bot.send_message(chat_id, f"{mensaje}. En breve comenzará el proceso, tenga un poco de paciencia.")

        # Iniciamos el proceso
        # Función para actualizar el mensaje dinámicamente
        def update_progress(text, percentage):
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"{text}\n[{'█' * int(percentage // 5)}{'░' * (20 - int(percentage // 5))}] {percentage}%"
            )

        try:
            # Llamar al proceso principal pasando la función de actualización
            iniciar_en_hilo(chat_id, update_progress)
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text="✅ ¡Proceso completado!\n[████████████████████] 100%"
            )
        except Exception as e:
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"❌ Error durante el proceso: {str(e)}"
            )

    else:
        bot.send_message(chat_id, mensaje)  # Envía el mensaje de error al usuario

@app.route("/")
def home():
    return "Bot funcionando"

# Ruta de Flask para el webhook
@app.route(f"/{TOKEN}", methods=["POST"])  # <-- Agrega la barra al final
def receive_update():
    json_update = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_update)
    bot.process_new_updates([update])
    return "OK", 200

# Establece la webhook al iniciar
@app.route("/set_webhook", methods=["GET", "POST"])
def set_webhook():
    success = bot.set_webhook(url=WEBHOOK_URL + f"/{TOKEN}")
    if success:
        return "Webhook configurada correctamente", 200
    else:
        return "Fallo al configurar el webhook", 500

# Elimina la webhook si es necesario
@app.route("/delete_webhook", methods=["GET", "POST"])
def delete_webhook():
    bot.delete_webhook()
    return "Webhook eliminada correctamente", 200
