# Módulos de python
import os
# Módulos de terceros
import psycopg2

# Configuraciones de la base de datos
name = os.getenv('db_name')
user = os.getenv('db_user')
passwrd = os.getenv('db_password')
host = os.getenv('db_host')
port = 5432
