# -*- coding: utf-8 -*-
from functools import wraps
import logging
from odoo import http, _
from odoo.http import request, Response
from werkzeug.urls import url_join
from datetime import datetime
import logging
from odoo.exceptions import AccessError, ValidationError, UserError, MissingError
from datetime import datetime, timedelta
import werkzeug
from psycopg2.errors import InvalidDatetimeFormat

_logger = logging.getLogger(__name__)


def api_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            return {"status": 422, "message": _("Missing key: {e}").format(e=e)}
        # except InvalidDatetimeFormat:
        #     return {"status": 400,"message": _("Invalid date format provided, it should be 'YYYY-MM-DD'"),}
        except ValueError as e:
            return {"status": 400, "message": _("Invalid value: {e}").format(e=e)}
        except AccessError:
            return {"status": 403,"message": _("You do not have the necessary permissions to perform this action."),}
        except MissingError as e:
            return {"status": 404, "message": "Record not found: {e}".format(e=e)}
        except UserError as e:
            return {"status": 409, "message": _("Validation error: {e}").format(e=e)}
        except Exception as e:
            return {"status": 500, "message": str(e)}

    return wrapper
