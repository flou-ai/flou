from pathlib import Path
import pytest
from alembic.config import Config
from alembic import command
from sqlalchemy.orm import Session

from flou.database import engine

@pytest.fixture(scope='session')
def alembic_config():
    """Return Alembic configuration object."""
    # Locate the alembic.ini file
    flou_dir = Path(__file__).parent / '../flou'
    alembic_ini_path = flou_dir / 'alembic.ini'
    config = Config(alembic_ini_path)
    config.set_main_option("script_location", str(flou_dir / 'migrations'))
    config.set_main_option("prepend_sys_path", str(flou_dir))
    return config

@pytest.fixture(scope='session')
def setup_database(alembic_config):
    """Set up the database schema using Alembic migrations."""

    # Run Alembic migrations to upgrade to the latest revision
    command.upgrade(alembic_config, "head")

    yield

    # Optionally, you can run downgrades or clean up here
    # For SQLite, since the database file is temporary, it will be deleted automatically

@pytest.fixture(scope='function', autouse=True)
def session(setup_database):
    """
    Create a new database session for a test.
    Rollback any changes after the test completes.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.rollback()
    session.close()
