"""
Create 'resources' table
"""

from yoyo import step

__depends__ = {'20221109_01_HbD5F-add-resource-meta-field-to-resource-categories-field'}

steps = [
    step(
        """
        CREATE TABLE IF NOT EXISTS resources(
            group_id TEXT NOT NULL,
            resource_id TEXT PRIMARY KEY,
            resource_name TEXT NOT NULL,
            resource_category_id TEXT NOT NULL,
            FOREIGN KEY(group_id) REFERENCES groups(group_id),
            FOREIGN KEY(resource_category_id) REFERENCES resource_categories(resource_category_id)
        ) WITHOUT ROWID
        """,
        "DROP TABLE IF EXISTS resources")
]