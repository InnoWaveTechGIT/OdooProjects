from odoo import http
from functools import wraps
from odoo.http import request
from .error_handler import api_error_handler
from .safe_json_body import safe_json_body
from odoo.exceptions import AccessError, ValidationError, UserError, MissingError

"""
This is a simplified template to mimic ruby on rails before and after actions in controllers
"""
class BaseController(http.Controller):
    _before_actions = []
    _after_actions = []

    @classmethod
    def before_action(cls, method_name, only=None, except_=None):
        cls._before_actions.append(
            {
                "method": method_name,
                "only": set(only or []),
                "except": set(except_ or []),
            }
        )

    @classmethod
    def after_action(cls, method_name, only=None, except_=None):
        cls._after_actions.append(
            {
                "method": method_name,
                "only": set(only or []),
                "except": set(except_ or []),
            }
        )

    @staticmethod
    def apply_action_hooks(method):
        """Wrap methods with before and after actions."""

        @wraps(method)
        def wrapper(self, *args, **kwargs):
            method_name = method.__name__
            cls = self.__class__
            # Execute before actions
            for action in cls._before_actions:
                if (not action["only"] or method_name in action["only"]) and method_name not in action["except"]:
                    getattr(self, action["method"])()
                    
            # Execute the original method
            result = method(self, *args, **kwargs)

            # Execute after actions
            for action in cls._after_actions:
                if ( not action["only"] or method_name in action["only"]) and method_name not in action["except"]:
                    getattr(self, action["method"])()

            return result
        return wrapper

    @classmethod
    def route(cls, *args, **kwargs):
        def decorator(method):
            method = http.route(*args, **kwargs)(method)
            method = safe_json_body(api_error_handler(cls.apply_action_hooks(method)))
            return method
        return decorator

    
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Register actions defined in class variables
        for action in getattr(cls, "__before_actions__", []):
            cls.before_action(**action)
        for action in getattr(cls, "__after_actions__", []):
            cls.after_action(**action)