from odoo import http
from werkzeug.urls import url_join
from odoo.http import request, Response, JsonRPCDispatcher
import hmac
import hashlib
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from odoo.exceptions import AccessDenied
import werkzeug
from werkzeug.exceptions import (
    HTTPException,
    BadRequest,
    Forbidden,
    NotFound,
    InternalServerError,
)


class CustomJsonResponse(JsonRPCDispatcher):
    def dispatch(self, endpoint, args):
        """
        modify original function to remove error on empty json body
        """
        try:
            self.jsonrequest = self.request.get_json_data()
        except ValueError as exc:
            self.jsonrequest = {}
        try:
            self.request_id = self.jsonrequest.get("id")
        except ValueError as exc:
            werkzeug.exceptions.abort(Response("Invalid JSON data", status=400))
        except AttributeError as exc:
            werkzeug.exceptions.abort(Response("Invalid JSON-RPC data", status=400))
        self.request.params = dict(self.jsonrequest.get("params", {}), **args)
        ctx = self.request.params.pop("context", None)
        if ctx is not None and self.request.db:
            self.request.update_context(**ctx)
        if self.request.db:
            result = self.request.registry["ir.http"]._dispatch(endpoint)
            return self._response(result)
        else:
            result = endpoint(**self.request.params)
            return self._response_endpoint(result)
        # return self._response(result)

    def _response_endpoint(self, result=None, error=None):
        response = {"jsonrpc": "2.0", "id": self.request_id}
        if error is not None:
            response["error"] = error
            if isinstance(response, dict):
                return self.request.make_json_response(response, status=500)
        if result is not None:
            response["result"] = result
            if (
                isinstance(response, dict)
                and isinstance(response["result"], dict)
                and "status" in response["result"]
            ):
                code = response["result"]["status"]
                return self.request.make_json_response(response, status=code)

        return self.request.make_json_response(response)
