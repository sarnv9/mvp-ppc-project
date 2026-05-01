from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()
url = os.getenv("URL_DATABASE")

print(f"Intentando conectar a: {url}")

try:
    engine = create_engine(url)
    # Intenta realizar una conexión física
    with engine.connect() as connection:
        print("✅ ¡Conexión exitosa a la base de datos!")
except Exception as e:
    print(f"❌ Error de conexión: {e}")