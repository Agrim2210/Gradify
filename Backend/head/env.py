import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from app.modules.workspace.infra.database import models
from alembic import context
from app.modules.auth.infra.persistent.models.models import UserModel, PendingRegistrationModel
from app.infra.database.base import Base
from app.modules.auth.infra.persistent.models.verification_token_model import VerificationTokenModel
from app.modules.auth.infra.persistent.models.outbox_model import OutboxEventModel
from app.modules.auth.infra.persistent.models.password_reset_token_model import PasswordResetTokenModel
from app.modules.auth.infra.persistent.models.user_model import UserModel
from app.modules.workspace.infra.database.membership_sql import WorkspaceMembershipModel
from app.modules.workspace.infra.database.invitation_sql import WorkspaceInvitationModel
from app.modules.workspace.infra.database.classroom_models import (
    ClassroomModel,
    ClassroomMembershipModel,
    ClassroomInvitationModel,
    AssignmentGradeModel,
)
from app.modules.documents.infra.database.note_model import ClassroomNoteModel

config = context.config

env_db_url = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
if env_db_url:
    if env_db_url.startswith("postgres://"):
        env_db_url = env_db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif env_db_url.startswith("postgresql://") and not env_db_url.startswith("postgresql+psycopg"):
        env_db_url = env_db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    if "+asyncpg" in env_db_url:
        env_db_url = env_db_url.replace("+asyncpg", "+psycopg")
    config.set_main_option("sqlalchemy.url", env_db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    url = config.get_main_option("sqlalchemy.url")
    if url:
        configuration["sqlalchemy.url"] = url
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
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
