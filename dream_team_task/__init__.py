
from . import models
from . import controllers
from .models.websocket_server import start_websocket_thread

def _start_websocket():
    start_websocket_thread()

_start_websocket()
