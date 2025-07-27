from odoo import models, fields
from .websocket_server import WebSocketServer
import asyncio
import threading
import json
from odoo import _
class StockQuant(models.Model):
    _inherit = 'stock.quant'

    def _send_ws_update(self):
        server = WebSocketServer()
        data = {
            'product_id': self.product_id.id,
            'product_name': self.product_id.name,
            'quantity': self.quantity,
            'location': self.location_id.complete_name
        }

        # Run in background thread
        def send_update():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(server.broadcast(data))
            loop.close()

        threading.Thread(target=send_update).start()

    def write(self, vals):
        res = super().write(vals)
        print(' x>>>> Quantity ')
        if 'quantity' in vals:
            x= self._send_ws_update()

        return res
