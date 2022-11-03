"""Test the auth database initialisation migration."""
from contextlib import closing

import pytest
import sqlite3

from gn3.migrations import get_migration, apply_migrations, rollback_migrations
from tests.unit.conftest import (
    apply_single_migration, rollback_single_migration)

migration_path = "migrations/auth/20221103_01_js9ub-initialise-the-auth-entic-oris-ation-database.py"

@pytest.mark.unit_test
def test_initialise_the_database(auth_testdb):
    with closing(sqlite3.connect(auth_testdb)) as conn, closing(conn.cursor()) as cursor:
        cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'")
        result = cursor.fetchall()
        assert "users" not in [row[0] for row in cursor.fetchall()]
        apply_single_migration(auth_testdb, get_migration(migration_path))
        cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'")
        assert "users" in [row[0] for row in cursor.fetchall()]

@pytest.mark.unit_test
def test_rollback_initialise_the_database(auth_testdb):
    with closing(sqlite3.connect(auth_testdb)) as conn, closing(conn.cursor()) as cursor:
        apply_single_migration(auth_testdb, get_migration(migration_path))
        rollback_single_migration(auth_testdb, get_migration(migration_path))
        cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'")
        assert "users" not in [row[0] for row in cursor.fetchall()]
