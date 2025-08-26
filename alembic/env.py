from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# --- CONFIGURACIÓN DE RUTAS ---
# Añadimos la carpeta src al path para importar módulos internos
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# --- IMPORTAMOS LA BASE Y MODELOS ---
from src.core.database import Base, engine
from src import models  # Asegúrate de que src/models/__init__.py importe todos los modelos

# --- CONFIGURACIÓN ALEMBIC ---
config = context.config

# Configuración de logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadatos para autogenerar migraciones
target_metadata = Base.metadata

def run_migrations_offline():
    """Ejecuta migraciones sin conexión activa (genera SQL en consola/archivo)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, compare_type=True
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Ejecuta migraciones en una conexión activa a la DB."""
    connectable = engine

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, compare_type=True
        )

        with context.begin_transaction():
            context.run_migrations()

# --- EJECUCIÓN ---
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
