# Usar una imagen base ligera de Python
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9

# Establecer el directorio de trabajo
WORKDIR /app

# Copiar dependencias del proyecto
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Playwright y los navegadores
RUN playwright install && playwright install-deps

# Copiar la aplicación
COPY . .

CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:8080"]
