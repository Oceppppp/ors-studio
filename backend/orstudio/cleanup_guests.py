"""Scheduled cleanup for expired guest workspaces."""
from pathlib import Path

from alembic import command
from alembic.config import Config

from . import cloud_store


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    command.upgrade(Config(str(project_root / "alembic.ini")), "head")
    removed = cloud_store.delete_expired_guests()
    print(f"Purged {removed} expired guest workspace(s).")


if __name__ == "__main__":
    main()
