"""Test migrations that create tables"""
from contextlib import closing

import pytest
import sqlite3

from gn3.migrations import get_migration, apply_migrations, rollback_migrations
from tests.unit.auth.conftest import (
    apply_single_migration, rollback_single_migration, migrations_up_to)

migrations_and_tables = (
    ("20221103_01_js9ub-initialise-the-auth-entic-oris-ation-database.py",
     "users"),
    ("20221103_02_sGrIs-create-user-credentials-table.py", "user_credentials"),
    ("20221108_01_CoxYh-create-the-groups-table.py", "groups"),
    ("20221108_02_wxTr9-create-privileges-table.py", "privileges"),
    ("20221108_03_Pbhb1-create-resource-categories-table.py", "resource_categories"),
    ("20221110_01_WtZ1I-create-resources-table.py", "resources"),
    ("20221110_02_z1dWf-create-mrna-resources-table.py", "mrna_resources"),
    ("20221110_03_ka3W0-create-phenotype-resources-table.py", "phenotype_resources"),
    ("20221110_04_6PRFQ-create-genotype-resources-table.py", "genotype_resources"),
    ("20221110_05_BaNtL-create-roles-table.py", "roles"),
    ("20221110_06_Pq2kT-create-generic-roles-table.py", "generic_roles"))

@pytest.mark.unit_test
@pytest.mark.parametrize("migration_file,the_table", migrations_and_tables)
def test_create_table(
        auth_testdb_path, auth_migrations_dir, backend, all_migrations,
        migration_file, the_table):
    """
    GIVEN: A database migration script to create table, `the_table`
    WHEN: The migration is applied
    THEN: Ensure that the table `the_table` is created
    """
    migration_path=f"{auth_migrations_dir}/{migration_file}"
    older_migrations = migrations_up_to(migration_path, auth_migrations_dir)
    apply_migrations(backend, older_migrations)
    with closing(sqlite3.connect(auth_testdb_path)) as conn, closing(conn.cursor()) as cursor:
        cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'")
        result_before_migration = cursor.fetchall()
        apply_single_migration(backend, get_migration(migration_path))
        cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'")
        result_after_migration = cursor.fetchall()

    rollback_migrations(backend, older_migrations)
    assert the_table not in [row[0] for row in result_before_migration]
    assert the_table in [row[0] for row in result_after_migration]

@pytest.mark.unit_test
@pytest.mark.parametrize("migration_file,the_table", migrations_and_tables)
def test_rollback_create_table(
        auth_testdb_path, auth_migrations_dir, backend, migration_file,
        the_table):
    """
    GIVEN: A database migration script to create the table `the_table`
    WHEN: The migration is rolled back
    THEN: Ensure that the table `the_table` no longer exists
    """
    migration_path=f"{auth_migrations_dir}/{migration_file}"
    older_migrations = migrations_up_to(migration_path, auth_migrations_dir)
    apply_migrations(backend, older_migrations)
    with closing(sqlite3.connect(auth_testdb_path)) as conn, closing(conn.cursor()) as cursor:
        apply_single_migration(backend, get_migration(migration_path))
        cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'")
        result_after_migration = cursor.fetchall()
        rollback_single_migration(backend, get_migration(migration_path))
        cursor.execute("SELECT name FROM sqlite_schema WHERE type='table'")
        result_after_rollback = cursor.fetchall()

    rollback_migrations(backend, older_migrations)
    assert the_table in [row[0] for row in result_after_migration]
    assert the_table not in [row[0] for row in result_after_rollback]
