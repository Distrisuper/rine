import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from alembic.config import Config
from alembic import command
from sqlalchemy import text

# Configurar la URL de la base de datos de test antes de importar nada de la app
TEST_DB_URL = "sqlite:////tmp/rine_test.db"
os.environ["DATABASE_URL"] = TEST_DB_URL

from infrastructure.api.main import app
from infrastructure.db import database

@pytest.fixture(scope="session")
def run_migrations():
    # Asegurarnos de que el directorio /tmp existe (o el path que elijamos)
    alembic_cfg = Config("alembic.ini") # Path relativo a la raíz del proyecto
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    
    # Crear tablas desde cero para el test si es SQLite
    engine = create_engine(TEST_DB_URL)
    SQLModel.metadata.create_all(engine)
    yield engine
    # Opcional: eliminar el archivo db al terminar
    if os.path.exists("/tmp/rine_test.db"):
        os.remove("/tmp/rine_test.db")

@pytest.fixture(scope="function")
def test_engine(run_migrations):
    engine = run_migrations
    # Inyectar el motor de test en la infraestructura
    database.engine = engine
    yield engine

@pytest.fixture(scope="function")
def client(test_engine):
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function", autouse=True)
def clean_tables(test_engine):
    with test_engine.connect() as conn:
        # Desactivar constraints para limpiar en orden (importante en Postgres, en SQLite no tanto)
        conn.execute(text("DELETE FROM printer_channels"))
        conn.execute(text("DELETE FROM printers"))
        conn.execute(text("DELETE FROM channels"))
        conn.execute(text("DELETE FROM templates"))
        conn.execute(text("DELETE FROM print_jobs"))
        conn.commit()
