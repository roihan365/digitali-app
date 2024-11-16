from odoo import models
from odoo.http import request
from werkzeug.exceptions import BadRequest

class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _auth_method_tokenUnit(cls):
        # Allow OPTIONS requests without API key
        if request.httprequest.method == 'OPTIONS':
            return  # Skip authentication for OPTIONS requests
        
        token = request.httprequest.headers.get("X-Unit-Token")
        if not token:
            raise BadRequest("Authorization header with token missing")

        # Strip 'Bearer ' prefix if present
        if token.startswith("Bearer "):
            return BadRequest("Invalid token format")

        # Check the tojen key against the database
        allowed_keys = ["dig-032903", "haf-032903", "gibs-032903"]
        
        # Validate that the API key matches one of the allowed keys
        if token not in allowed_keys:
            raise BadRequest("API key invalid")

    @classmethod
    def _auth_method_apikey(cls):
        # Allow OPTIONS requests without API key
        if request.httprequest.method == 'OPTIONS':
            return  # Skip authentication for OPTIONS requests
        
        api_key = request.httprequest.headers.get("X-ODOO-API-KEY")
        if not api_key:
            raise BadRequest("Authorization header with API key missing")

        # Strip 'Bearer ' prefix if present
        if api_key.startswith("Bearer "):
            api_key = api_key[len("Bearer "):]

        # Check the API key against the database
        user_id = request.env["res.users.apikeys"]._check_credentials(scope="rpc", key=api_key)
        if not user_id:
            raise BadRequest("API key invalid")

        # Update the environment with the user ID
        request.update_env(user=user_id)
