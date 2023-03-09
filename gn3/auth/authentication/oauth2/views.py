"""Endpoints for the oauth2 server"""
import uuid

from flask import Response, Blueprint, current_app as app

from gn3.auth.authorisation.errors import ForbiddenAccess

from .resource_server import require_oauth
from .endpoints.revocation import RevocationEndpoint
from .endpoints.introspection import IntrospectionEndpoint

auth = Blueprint("auth", __name__)

@auth.route("/register-client", methods=["GET", "POST"])
def register_client():
    """Register an OAuth2 client."""
    return "WOULD REGISTER ..."

@auth.route("/delete-client/<uuid:client_id>", methods=["GET", "POST"])
def delete_client(client_id: uuid.UUID):
    """Delete an OAuth2 client."""
    return f"WOULD DELETE OAUTH2 CLIENT {client_id}."

@auth.route("/authorise", methods=["GET", "POST"])
def authorise():
    """Authorise a user"""
    return "WOULD AUTHORISE THE USER."

@auth.route("/token", methods=["POST"])
def token():
    """Retrieve the authorisation token."""
    server = app.config["OAUTH2_SERVER"]
    return server.create_token_response()

@auth.route("/revoke", methods=["POST"])
def revoke_token():
    """Revoke the token."""
    return app.config["OAUTH2_SERVER"].create_endpoint_response(
        RevocationEndpoint.ENDPOINT_NAME)

@auth.route("/introspect", methods=["POST"])
@require_oauth("introspect")
def introspect_token() -> Response:
    """Provide introspection information for the token."""
    # This is dangerous to provide publicly
    authorised_clients = app.config.get(
        "OAUTH2_CLIENTS_WITH_INTROSPECTION_PRIVILEGE", [])
    with require_oauth.acquire("introspect") as the_token:
        if the_token.client.client_id in authorised_clients:
            return app.config["OAUTH2_SERVER"].create_endpoint_response(
                IntrospectionEndpoint.ENDPOINT_NAME)

    raise ForbiddenAccess("You cannot access this endpoint")
