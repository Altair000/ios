# Usar una imagen base ligera de Python con Uvicorn y Gunicorn
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar las dependencias del proyecto
COPY requirements.txt requirements.txt

# Instalar las dependencias desde el archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Playwright y los navegadores
RUN playwright install && playwright install-deps

# Copiar la aplicación al contenedor
COPY . .

# Exponer el puerto en el que FastAPI escuchará
EXPOSE 8080

# Comando para iniciar la aplicación con Uvicorn
CMD ["uvicorn", "bot:app", "--host", "0.0.0.0", "--port", "8080"]
