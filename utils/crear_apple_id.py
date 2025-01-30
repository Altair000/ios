# Bibliotecas de python
import time

# Bibliotecas externas
import threading
from collections import deque
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright, TimeoutError

# Bibliotecas locales
from configs.twilios import numero_twilio_formateado
from utils.db import obtener_datos_de_apple_id
from utils.handlers import iniciar_manejador_captcha as manejar_captcha, iniciar_manejador_otp_mail as manejar_otp_mail

# Variables globales
HECHO = False # Constante que controla el flujo del bot
REINICIAR = False # Constante que controla si el bucle principal debe de reiniciarse
# Código
"""
Función que manejará el proceso de Creación de Apple Id
"""
def iniciar(chat_id, update_progress):
    datos = obtener_datos_de_apple_id(chat_id)

    # Asignar cada valor de la tupla a variables
    NOMBRE, APELLIDO, FECHA, EMAIL, PASS = datos

    # Convertir a string con formato "DD/MM/YYYY"
    FECHA_STR = FECHA.strftime('%d/%m/%Y')

    # Ahora sí se puede dividir
    DIA, MES, ANO = FECHA_STR.split('/')

    # Continuamos con el codigo
    total_steps = 18  # Ajusta según la cantidad de pasos aproximados
    step_count = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        iphone_13 = p.devices['iPhone 13']
        context = browser.new_context(**iphone_13)
        page = context.new_page()

        try:
            # Navegar a la página inicial
            step_count += 1
            update_progress("Navegando a la página inicial...", (step_count / total_steps) * 100)
            time.sleep(1)  # Simula el tiempo necesario

            page.goto('https://account.apple.com/account', timeout=60000)
            page.wait_for_load_state("load")

            # Buscar el iframe
            # Paso 2: Buscar el iframe
            step_count += 1
            update_progress("Buscando el iframe...", (step_count / total_steps) * 100)
            time.sleep(1)

            iframe_locator = page.locator("iframe[title='Crear tu cuenta de Apple']")
            iframe = iframe_locator.content_frame

            # Llenar formulario de registro
            # Nombre
            # Paso 3: Introducir primer nombre
            step_count += 1
            update_progress("Introduciendo primer nombre...", (step_count / total_steps) * 100)
            time.sleep(1)

            iframe.locator('input[name="firstName"]').click()
            iframe.locator('input[name="firstName"]').type(NOMBRE, delay=150)

            # Apellido
            # Paso 4: Introducir segundo nombre
            step_count += 1
            update_progress("Introduciendo apellido...", (step_count / total_steps) * 100)
            time.sleep(1)

            iframe.locator('input[name="lastName"]').click()
            iframe.locator('input[name="lastName"]').type(APELLIDO, delay=150)

            # País
            # Paso 5: Seleccionar país
            step_count += 1
            update_progress("Seleccionando país USA...", (step_count / total_steps) * 100)
            time.sleep(1)

            iframe.locator('select[name="countrySelect"]').select_option('USA') # Siempre será USA

            # Fecha
            # Paso 6: Introducir fecha de nacimiento
            step_count += 1
            update_progress("Estableciendo fecha de nacimiento...", (step_count / total_steps) * 100)
            time.sleep(1)

            iframe.locator('select[data-testid="select-day"]').select_option(DIA) # Día
            iframe.locator('select[data-testid="select-month"]').select_option(MES) # Mes
            iframe.locator('select[data-testid="select-year"]').select_option(ANO) # Año

            # Correo Electrónico
            # Paso 7: Introducir correo
            step_count += 1
            update_progress("Introduciendo correo electrónico...", (step_count / total_steps) * 100)
            time.sleep(1)

            iframe.locator('input[name="appleId"]').click()
            iframe.locator('input[name="appleId"]').type(EMAIL, delay=150)

            # Contraseña
            # Paso 8: Introducir contraseña
            step_count += 1
            update_progress("Introduciendo contraseña...", (step_count / total_steps) * 100)
            time.sleep(1)

            iframe.locator('input[name="password"]').click()
            iframe.locator('input[name="password"]').type(PASS, delay=150)

            # Confirmar contraseña
            # Paso 9: Confirmar contraseña
            step_count += 1
            update_progress("Confirmando...", (step_count / total_steps) * 100)
            time.sleep(1)

            iframe.locator('input[name="confirmPassword"]').click()
            iframe.locator('input[name="confirmPassword"]').type(PASS, delay=150)

            # Número de teléfono
            # Paso 10: Establecer número
            step_count += 1
            update_progress("Estableciendo Número telefónico...", (step_count / total_steps) * 100)
            time.sleep(1)

            iframe.locator('input[name="phoneNumber"]').click()
            iframe.locator('input[name="phoneNumber"]').type(numero_twilio_formateado, delay=150)

            # Obtención de Captcha
            # Paso 11: Obtener captcha
            step_count += 1
            update_progress("Obteniendo Captcha...", (step_count / total_steps) * 100)
            time.sleep(1)
            stop_event = threading.Event() # Maneja la detención del hilo en caso de inactividad.

            # Obtenemos el captcha desde el html de la página
            images = iframe.locator("img").all()
            for image in images:
                alt_text = image.get_attribute("alt")
                if "Imagen de verificación" in alt_text:
                    captcha_encoded = image.get_attribute("src")
                    break

            if captcha_encoded and captcha_encoded.startswith("data:image"):
                captcha_encoded = captcha_encoded.split(",")[1]  # Eliminar prefijo "data:image/png;base64,"

            captcha, captcha_resolved = manejar_captcha(chat_id, stop_event, captcha_encoded)

            if not captcha_resolved:
                return  # Salir si el usuario no respondió a tiempo

            # Resolución del captcha
            # Paso 12: Resolver Captcha
            step_count += 1
            update_progress("Introduciendo CAPTCHA...", (step_count / total_steps) * 100)
            time.sleep(1)

            iframe.locator('input[name="captcha"]').click()
            iframe.locator('input[name="captcha"]').type(captcha, delay=100)

            time.sleep(1) # Esperamos a que se procese la información

            if iframe.locator('button:has-text("Continuar")').is_enabled():
                iframe.locator('button:has-text("Continuar")').click()
            else:
                return

            # Esperar respuesta de validación
            time.sleep(2)  # Ajustar según sea necesario

            # Manejo de respuesta XHR
            # Paso 13: Manejar respuesta XHR
            step_count += 1
            update_progress("Manejando respuesta...", (step_count / total_steps) * 100)
            time.sleep(1)

            response_text = None  # Inicializar la variable para evitar referencias antes de asignación
            try:
                # Intentar localizar el primer posible error
                response = iframe.locator('div[class="text text-typography-body-reduced text-color-glyph-red"]')
                response.wait_for()  # Esperar hasta que el elemento esté disponible
                response_text = response.inner_text()
            except TimeoutError:
                try:
                    # Intentar localizar el segundo posible error
                    captcha_err_response = iframe.locator('span[class="visuallyhidden"]')
                    captcha_err_response.wait_for()  # Esperar hasta que el elemento esté disponible
                    response_text = captcha_err_response.inner_text()
                except TimeoutError:
                    # Ningún error encontrado; respuesta XHR o estado normal
                    response_text = None
            finally:
                # Determinar el mensaje según el texto obtenido
                if response_text == "En este momento, no se puede crear tu cuenta.":
                    text = f"{response_text}. Esto es un error crítico. Por favor inténtelo de nuevo, en caso de seguir fallando cambie de número o contacte a soporte."
                elif response_text == "Error de verificación de seguridad:":
                    text = f"{response_text}. Esto es un error de captcha, Inténtelo de nuevo."
                else:
                    # Manejo de respuesta XHR o estado normal
                    text = "Procesando..."  # Texto por defecto
                    timer = 1

            # Paso 14: Manejar respuesta XHR
            step_count += 1
            update_progress(text, (step_count / total_steps) * 100)
            time.sleep(timer)
            stop_event = threading.Event()  # Maneja la detención del hilo en caso de inactividad.

            email_otp, email_otp_resolved = manejar_otp_mail(chat_id, EMAIL, stop_event)

            if not email_otp_resolved:
                return  # Salir si el usuario no respondió a tiempo

            # Paso 15: Manejar proceso de verificación mail otp
            step_count += 1
            update_progress("Comenzamos proceso de verificación email...", (step_count / total_steps) * 100)
            time.sleep(1)

            iframe.locator(f'input[aria-label="Verificar dirección de correo electrónico Introduce el código de verificación enviado a: {EMAIL} Introduce el código de verificación Dígito 1"]').click()

            email_otp = list(str(email_otp))

            uno, dos, tres, cuatro, cinco, seis = email_otp

            iframe.locator(f'input[aria-label="Verificar dirección de correo electrónico Introduce el código de verificación enviado a: {EMAIL} Introduce el código de verificación Dígito 1"]').type(uno)
            time.sleep(0.5)
            iframe.locator('input[aria-label="Dígito 2"]').type(dos)
            time.sleep(0.5)
            iframe.locator('input[aria-label="Dígito 3"]').type(tres)
            time.sleep(0.5)
            iframe.locator('input[aria-label="Dígito 4"]').type(cuatro)
            time.sleep(0.5)
            iframe.locator('input[aria-label="Dígito 5"]').type(cinco)
            time.sleep(0.5)
            iframe.locator('input[aria-label="Dígito 6"]').type(seis)

            # Paso 16: Continuar después del proceso de mail otp
            step_count += 1
            update_progress("Continuando con el proceso...", (step_count / total_steps) * 100)
            time.sleep(1)

            iframe.locator('button:has-text("Continuar")').click()

            mail_otp_response_text = None
            try:
                mail_otp_response = iframe.locator('span[class="form-message"]')
                mail_otp_response.wait_for()
                mail_otp_response_text = f"{mail_otp_response.inner_text()}. Por favor inténtelo de nuevo."
            except:
                mail_otp_response_text = "OTP verificado correctamente, continuando con el proceso..."
                pass

            # Paso 17: Verificar validez del OTP
            step_count += 1
            update_progress(mail_otp_response_text, (step_count / total_steps) * 100)
            time.sleep(1)

            input()

            # Simular paso final
            step_count += 1
            update_progress("Finalizando creación de Apple ID...", (step_count / total_steps) * 100)
            time.sleep(1)

        except Exception as e:
            raise RuntimeError(f"Error en el proceso: {str(e)}")

"""
Función que manejará hilos por usuario con un máximo de 3
"""
# Lista para almacenar los hilos activos
active_threads = deque()

# Límite de hilos
MAX_THREADS = 3

# Función que maneja la creación del Apple ID en un hilo separado
def iniciar_en_hilo(chat_id, update_progress):
    # Verifica si hay espacio para un nuevo hilo
    if len(active_threads) >= MAX_THREADS:
        # Si ya hay 3 hilos activos, informa al usuario que espere
        update_progress("Se ha alcanzado el límite de hilos activos. Intenta de nuevo más tarde.", 0)
        return

    # Añadir el hilo actual a la lista de hilos activos
    thread = threading.Thread(target=iniciar, args=(chat_id, update_progress))
    active_threads.append(thread)

    # Iniciar el hilo
    thread.start()
