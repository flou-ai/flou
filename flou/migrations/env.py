import importlib
import pkgutil
from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool
from sqlalchemy.exc import InvalidRequestError

from alembic import context
from alembic_utils.replaceable_entity import register_entities
from alembic_utils.pg_trigger import PGTrigger
from alembic_utils.pg_function import PGFunction

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
import flou
from flou.database.models import Base
target_metadata = Base.metadata

# Function to dynamically import all `models.py` and `models/` from apps
def import_all_models():
    root_package = 'flou'
    alembic_utils_entities = []


    package = importlib.import_module(root_package)
    for importer, modname, ispkg in pkgutil.walk_packages(package.__path__, package.__name__ + '.'):
        if modname.endswith('.models'):
            models_module = importlib.import_module(modname)
            # look for PGTriggers which need to be manually added to
            # alembic_utils' `register_entitis`
            for _, variable in models_module.__dict__.items():

                if isinstance(variable, (PGTrigger, PGFunction, )):
                    # Ensure variable is not a subclass
                    if variable.__class__ in (PGTrigger, PGFunction, ):
                        alembic_utils_entities.append(variable)

    register_entities(alembic_utils_entities)  # register all entities

# setup models & triggers
try:
    import_all_models()  # add every model to the DeclarativeBase
except InvalidRequestError:
    pass  # don't break on tests

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


from flou.conf import settings
database_url = settings.database.url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = database_url
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_engine(
        database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
