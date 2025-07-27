from functools import wraps
from odoo.http import request


def safe_json_body(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            json_data = request.get_json_data()
            if not json_data:
                json_data = {}
        except Exception:
            json_data = {}

        # Pass the JSON data to the decorated function
        kwargs.update(json_data)
        return func(*args, **kwargs)

    return wrapper
