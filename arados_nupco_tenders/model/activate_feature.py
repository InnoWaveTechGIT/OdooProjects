from odoo import api, SUPERUSER_ID

def module_install(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    res_config_settings = env['res.config.settings']

    # Find the record and update the field value
    settings = res_config_settings.create({})
    settings.group_sale_delivery_address = True
