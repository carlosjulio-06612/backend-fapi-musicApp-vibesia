# File: alembic/env.py (Corrected and Final Version)

# --- START OF KEY MODIFICATION ---
import os
import sys

# Add the project root to Python path so it can find the 'app' package
# Go up one level from 'alembic' folder to project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# --- Import Base and ALL your application models ---
# Alembic needs to know them for the 'autogenerate' function.
from app.core.database import Base
from app.models.User import User
# If you have more models, import them here too.
# from app.models.Product import Product
# from app.models.Order import Order

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set target_metadata to your declarative Base's metadata.
# This is essential for 'autogenerate' to work.
target_metadata = Base.metadata

# ----- IMPORTANT VERIFICATION -----
# Make sure your Base in app/core/database.py defines the schema.
# Example:
# from sqlalchemy.orm import declarative_base
# from sqlalchemy import MetaData
#
# POSTGRES_SCHEMA = "vibesia_schema"
# metadata_obj = MetaData(schema=POSTGRES_SCHEMA)
# Base = declarative_base(metadata=metadata_obj)
# -----------------------------------


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Support schema in offline mode
        version_table_schema=target_metadata.schema,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # Configuration for Alembic to handle your schema correctly
            include_schemas=True,
            version_table_schema=target_metadata.schema
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()