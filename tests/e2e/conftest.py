import os
import pytest
from sqlmodel import SQLModel, create_engine, Session
from alembic.config import Config
from alembic import command
from sqlalchemy import text

os.environ["DATABASE_URL"] = "sqlite:////app/.data/rine_test.db"

from domain.entities.print_job import PrintJob
from infrastructure.db import database

TEST_DB_URL = "sqlite:////app/.data/rine_test.db"


@pytest.fixture(scope="session")
def run_migrations():
    alembic_cfg = Config("/app/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    
    try:
        command.upgrade(alembic_cfg, "head")
    except Exception:
        from alembic.script import ScriptDirectory
        from alembic import context
        script = ScriptDirectory.from_config(alembic_cfg)
        revisions = list(script.walk_revisions())
        head_revision = revisions[0].revision if revisions else "head"
        command.stamp(alembic_cfg, head_revision)


@pytest.fixture(scope="function")
def test_engine(run_migrations):
    engine = create_engine(TEST_DB_URL, echo=False)
    database.engine = engine
    yield engine
    database.engine = create_engine("sqlite:////app/.data/rine.db", echo=False)


@pytest.fixture(scope="function", autouse=True)
def clean_tables(test_engine):
    with test_engine.connect() as conn:
        conn.execute(text("DELETE FROM print_jobs"))
        conn.commit()
