"""Test resource-management functions"""
import uuid

import pytest

from gn3.auth.authorisation.groups import Group
from gn3.auth.authorisation.resources import (
    Resource, create_resource, ResourceCategory)

from tests.unit.auth import conftest

group = Group(uuid.UUID("9988c21d-f02f-4d45-8966-22c968ac2fbf"), "TheTestGroup")
resource_category = ResourceCategory(
    uuid.UUID("fad071a3-2fc8-40b8-992b-cdefe7dcac79"), "mrna", "mRNA Dataset")
create_resource_failure = {
    "status": "error",
    "message": "Unauthorised: Could not create resource"
}
uuid_fn = lambda : uuid.UUID("d32611e3-07fc-4564-b56c-786c6db6de2b")

@pytest.mark.unit_test
@pytest.mark.parametrize(
    "user,expected",
    tuple(zip(
        conftest.TEST_USERS,
        (Resource(
            group, uuid.UUID("d32611e3-07fc-4564-b56c-786c6db6de2b"),
            "test_resource", resource_category),
         create_resource_failure,
         create_resource_failure,
         create_resource_failure,
         create_resource_failure))))
def test_create_resource(mocker, test_app, test_users_in_group, user, expected):
    """Test that resource creation works as expected."""
    mocker.patch("gn3.auth.authorisation.resources.uuid4", uuid_fn)
    conn, _group, _users = test_users_in_group
    with test_app.app_context() as flask_context:
        flask_context.g.user = user
        assert create_resource(conn, "test_resource", resource_category) == expected
