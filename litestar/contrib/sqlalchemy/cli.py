from __future__ import annotations

from typing import TYPE_CHECKING

import anyio

from litestar.cli._utils import RICH_CLICK_INSTALLED, LitestarGroup
from litestar.contrib.sqlalchemy.alembic import commands as db_utils
from litestar.exceptions import LitestarException

if TYPE_CHECKING:
    from litestar import Litestar
    from litestar.contrib.sqlalchemy.plugins.init.config.asyncio import AlembicAsyncConfig
    from litestar.contrib.sqlalchemy.plugins.init.config.sync import AlembicSyncConfig


if TYPE_CHECKING or not RICH_CLICK_INSTALLED:
    from click import group, option
else:
    from rich_click import group, option


@group(cls=LitestarGroup, name="database")
def database_group() -> None:
    """Manage SQLAlchemy database components."""


def get_alembic_config(app: Litestar) -> AlembicAsyncConfig | AlembicSyncConfig:
    config: AlembicAsyncConfig | AlembicSyncConfig | None = None
    for cli_plugin in app.cli_plugins:
        if hasattr(cli_plugin, "_alembic_config"):
            config = cli_plugin._alembic_config
    if config is None:
        raise LitestarException("Could not find SQLAlchemy configuration.")
    return config


@database_group.command(
    name="current-revision",
    help="Shows the current revision for the database.",
)
@option("--verbose", type=bool, help="Enable verbose output.", default=False, is_flag=True)
def show_database_revision(app: Litestar, verbose: bool) -> None:
    """Show current database revision."""

    config = get_alembic_config(app)
    anyio.run(db_utils.current, config.alembic_config, config.script_location, verbose)


@database_group.command(
    name="downgrade",
    help="Downgrade database to a specific revision.",
)
@option(
    "--revision",
    type=str,
    help="Revision to upgrade to",
    default="head",
)
@option("--sql", type=bool, help="Generate SQL output for offline migrations.", default=False, is_flag=True)
@option(
    "--tag",
    help="an arbitrary 'tag' that can be intercepted by custom env.py scripts via the .EnvironmentContext.get_tag_argument method.",
    type=str,
    default=None,
)
def downgrade_database(app: Litestar, revision: str | None, sql: bool, tag: str | None) -> None:
    """Downgrade the database to the latest revision."""

    config = get_alembic_config(app)
    anyio.run(db_utils.downgrade, config.alembic_config, config.script_location, revision, sql, tag)


@database_group.command(
    name="upgrade",
    help="Upgrade database to a specific revision.",
)
@option(
    "--revision",
    type=str,
    help="Revision to upgrade to",
    default="head",
)
@option("--sql", type=bool, help="Generate SQL output for offline migrations.", default=False, is_flag=True)
@option(
    "--tag",
    help="an arbitrary 'tag' that can be intercepted by custom env.py scripts via the .EnvironmentContext.get_tag_argument method.",
    type=str,
    default=None,
)
def upgrade_database(app: Litestar, revision: str | None, sql: bool, tag: str | None) -> None:
    """Upgrade the database to the latest revision."""

    config = get_alembic_config(app)
    anyio.run(db_utils.upgrade, config.alembic_config, config.script_location, revision, sql, tag)


@database_group.command(
    name="init",
    help="Initialize migrations for the project.",
)
@option(
    "--revision",
    type=str,
    help="Revision to upgrade to",
    default="head",
)
@option("--sql", type=bool, help="Generate SQL output for offline migrations.", default=False, is_flag=True)
@option(
    "--tag",
    help="an arbitrary 'tag' that can be intercepted by custom env.py scripts via the .EnvironmentContext.get_tag_argument method.",
    type=str,
    default=None,
)
def init_alembic(app: Litestar, revision: str | None, sql: bool, tag: str | None) -> None:
    """Upgrade the database to the latest revision."""

    config = get_alembic_config(app)
    anyio.run(db_utils.init, config.alembic_config, config.script_location, revision, sql, tag)
