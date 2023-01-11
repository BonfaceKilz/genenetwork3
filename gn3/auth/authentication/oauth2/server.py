"""Initialise the OAuth2 Server"""
import uuid
import datetime
from typing import Callable

from flask import Flask, current_app
from authlib.integrations.flask_oauth2 import AuthorizationServer
# from authlib.integrations.sqla_oauth2 import (
#     create_save_token_func, create_query_client_func)

from gn3.auth import db

from .models.oauth2client import client
from .models.oauth2token import OAuth2Token, save_token

from .grants.password_grant import PasswordGrant
# from .grants.authorisation_code_grant import AuthorisationCodeGrant

from .endpoints.revocation import RevocationEndpoint
from .endpoints.introspection import IntrospectionEndpoint

def create_query_client_func() -> Callable:
    """Create the function that loads the client."""
    def __query_client__(client_id: uuid.UUID):
        # use current_app rather than passing the db_uri to avoid issues
        # when config changes, e.g. while testing.
        with db.connection(current_app.config["AUTH_DB"]) as conn:
            return client(conn, client_id).maybe(None, lambda clt: clt) # type: ignore[misc]

    return __query_client__

def create_save_token_func(token_model: type) -> Callable:
    """Create the function that saves the token."""
    def __save_token__(token, request):
        with db.connection(current_app.config["AUTH_DB"]) as conn:
            save_token(
                conn, token_model(
                    token_id=uuid.uuid4(), client=request.client,
                    user=request.client.user,
                    **{
                        "refresh_token": None, "revoked": False,
                        "issued_at": datetime.datetime.now(),
                        **token
                    }))

    return __save_token__

def setup_oauth2_server(app: Flask) -> None:
    """Set's up the oauth2 server for the flask application."""
    server = AuthorizationServer()
    server.register_grant(PasswordGrant)
    # server.register_grant(AuthorisationCodeGrant)

    # register endpoints
    server.register_endpoint(RevocationEndpoint)
    server.register_endpoint(IntrospectionEndpoint)

    # init server
    server.init_app(
        app,
        query_client=create_query_client_func(),
        save_token=create_save_token_func(OAuth2Token))
    app.config["OAUTH2_SERVER"] = server