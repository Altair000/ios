# Usar una imagen base ligera de Python
FROM python:3.9-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para Playwright
RUN apt-get update && apt-get install -y \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxrandr2 \
    libxdamage1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libxshmfence1 \
    libgbm-dev \
    wget \
    gnupg \
    libstdc++6 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar Playwright y los navegadores
RUN pip install playwright && playwright install

# Copiar dependencias del proyecto
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar la aplicación
COPY . .

# Exponer un puerto para Flask u otros servidores web
EXPOSE 8080

# Comando para iniciar la aplicación
CMD ["python3", "bot.py"]