# Módulos de terceros
import psycopg2
# Módulos locales
from configs.db_config import *

DB_CONFIG = {
    'dbname': name,
    'user': user,
    'password': passwrd,
    'host': host,
    'port': port
}

def conectar_bd():
    """Crea una conexión con la base de datos."""
    return psycopg2.connect(**DB_CONFIG)

# Función para obtener los datos de la cuenta
def obtener_datos_usuario(user_id):
    """Consulta la información de la cuenta desde la base de datos."""
    try:
        conn = conectar_bd()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT nombre, apellido, contraseña, correo, fecha_nacimiento, telefono_personal
                FROM usuarios
                WHERE id_telegram = %s;
            """, (user_id,))
            datos = cur.fetchone()
        conn.close()
        return datos
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return None

def insertar_usuario(datos):
    """Inserta un usuario en la base de datos."""
    try:
        conn = conectar_bd()
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO usuarios (id_telegram, nombre, apellido, contraseña, correo, fecha_nacimiento, telefono_personal)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (datos['id_telegram'], datos['nombre'], datos['apellido'], datos['contrasena'], datos['correo'], datos['fecha_nacimiento'], datos['telefono_personal']))
            conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error al insertar usuario: {e}")
        return False

def obtener_datos_de_apple_id(user_id):
    """Consulta la información de la cuenta desde la base de datos."""
    try:
        conn = conectar_bd()
        with conn.cursor() as cur:
            cur.execute("""
            SELECT nombre, apellido, fecha_nacimiento, correo, contraseña
            FROM usuarios
            WHERE id_telegram = %s;
            """, (user_id,))
            datos = cur.fetchone()
        conn.close()
        return datos
    except Exception as e:
        print(f"Error al obtener datos: {e}")
        return None