import base64
from configs.bot_config import bot

# Variable para almacenar la solución del captcha
captcha_result = {"value": None}
# Variable para controlar si estamos esperando una respuesta al captcha
esperando_respuesta_captcha = False

# Manejador para la verificación del captcha
def iniciar_manejador_captcha(chat_id, stop_event, captcha_encoded):
    global esperando_respuesta_captcha

    # Decodificar y guardar el captcha
    captcha_decoded = base64.b64decode(captcha_encoded)
    captcha_path = f'captcha_{chat_id}.jpg'

    # Guardar la imagen del captcha
    with open(captcha_path, 'wb') as file:
        file.write(captcha_decoded)

    # Enviar la imagen del captcha al usuario
    msg = bot.send_photo(chat_id, open(f'captcha_{chat_id}.jpg', 'rb'), caption='Resuelva y envíeme el captcha')

    # Marcar que estamos esperando la respuesta
    esperando_respuesta_captcha = True

    # Función callback para manejar la respuesta
    def callback(msg):
        global esperando_respuesta_captcha
        captcha_solution = msg.text.strip()
        if captcha_solution:  # Verificar que la respuesta no esté vacía
            captcha_result["value"] = captcha_solution
            stop_event.set()  # Despertar el proceso de espera
            esperando_respuesta_captcha = False  # Ya no estamos esperando una respuesta
        else:
            bot.send_message(chat_id, "Por favor, ingrese una respuesta válida para el captcha.")

    # Registrar el manejador para la siguiente respuesta del usuario
    bot.register_next_step_handler(msg, callback)

    # Esperar respuesta o timeout (5 minutos)
    if not stop_event.wait(300):
        bot.send_message(chat_id, "Se ha cerrado el hilo por inactividad.")
        esperando_respuesta_captcha = False  # Terminar el estado de espera
        return None, False

    return captcha_result["value"], True


# Manejador general para todos los mensajes
@bot.message_handler(func=lambda message: esperando_respuesta_captcha)
def manejador_mensajes(message):
    chat_id = message.chat.id

    # Verificar si estamos esperando una respuesta de captcha
    if esperando_respuesta_captcha:
        # Si el mensaje es solo texto, lo procesamos como respuesta del captcha
        if message.text.strip():
            respuesta_captcha = message.text.strip()
            # Realizar alguna acción con la respuesta
            print(f"Captcha recibido: {respuesta_captcha}")
            bot.send_message(chat_id, "Gracias por enviar el captcha. El proceso continúa.")
        else:
            bot.send_message(chat_id, "No has enviado una respuesta válida. Por favor, resuelve el captcha.")
    else:
        # Este bloque no debería ser alcanzado ya que el handler está filtrado por `esperando_respuesta_captcha`
        bot.send_message(chat_id, "El bot no está procesando mensajes en este momento. Por favor, resuelva el captcha.")


"""
Handler para manejar el OTP del e-mail.
"""
otp_mail_result = {"value": None} # Variable para almacenar la solución del captcha
esperando_respuesta_otp_mail = False # Variable para manejar los mensajes en el momento correcto.

def iniciar_manejador_otp_mail(chat_id, email, stop_event):
    global esperando_respuesta_otp_mail

    msg = bot.send_message(chat_id, f"Por favor envieme el numero de confirmacion recibido en el correo electronico con direccion: {email}")
    esperando_respuesta_otp_mail = True

    # Función callback para manejar la respuesta
    def callback_otp(msg):
        global esperando_respuesta_otp_mail
        otp_mail = msg.text.strip()
        if otp_mail:  # Verificar que la respuesta no esté vacía
            otp_mail_result["value"] = otp_mail
            stop_event.set()  # Despertar el proceso de espera
            esperando_respuesta_otp_mail = False  # Ya no estamos esperando una respuesta
        else:
            bot.send_message(chat_id, "Por favor, ingrese una respuesta válida para el otp.")

    # Registrar el manejador para la siguiente respuesta del usuario
    bot.register_next_step_handler(msg, callback_otp)

    # Esperar respuesta o timeout (5 minutos)
    if not stop_event.wait(300):
        bot.send_message(chat_id, "Se ha cerrado el hilo por inactividad.")
        esperando_respuesta_otp_mail = False  # Terminar el estado de espera
        return None, False

    return otp_mail_result["value"], True

# Manejador general para todos los mensajes
@bot.message_handler(func=lambda message: esperando_respuesta_otp_mail)
def manejador_mensajes_otp(message):
    chat_id = message.chat.id

    # Verificar si estamos esperando una respuesta de captcha
    if esperando_respuesta_otp_mail:
        # Si el mensaje es solo texto, lo procesamos como respuesta del captcha
        if message.text.strip():
            respuesta_otp_mail = message.text.strip()
            # Realizar alguna acción con la respuesta
            print(f"Captcha recibido: {respuesta_otp_mail}")
            bot.send_message(chat_id, "Gracias por enviar el otp. El proceso continúa.")
        else:
            bot.send_message(chat_id, "No has enviado una respuesta válida. Por favor, responda al otp.")
    else:
        # Este bloque no debería ser alcanzado ya que el handler está filtrado por `esperando_respuesta_captcha`
        bot.send_message(chat_id, "El bot no está procesando mensajes en este momento. Por favor, responda al otp.")