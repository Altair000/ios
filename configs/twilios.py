# Módulos de python
import os
# Módulos de terceros
from twilio.rest import Client

# Tus credenciales de Twilio
account_sid = os.getenv('twilio_sid', 'AC15c214d3371b5bb0daa8d0f77a5ff9d2')
auth_token = os.getenv('twilio_token', 'f21f574ad2ddc0d299e452d3e71aac7c')
client = Client(account_sid, auth_token)

# Variable de Twilio
numero_twilio = '+1(815) 486-0694'
numero_twilio_formateado = '(815) 486-0694'