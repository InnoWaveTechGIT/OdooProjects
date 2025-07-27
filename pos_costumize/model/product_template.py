from odoo import models, fields , api, _
from odoo.exceptions import ValidationError


class Offer(models.Model):
    _inherit = 'pos.config'



    user_id = fields.Many2one('res.users', string='User', domain=lambda self: [('groups_id', 'in', [self.env.ref('base.group_user').id])])

class POSOrder(models.Model):
    _inherit = 'pos.order'



    user_id = fields.Many2one('res.users', related='session_id.config_id.user_id')

