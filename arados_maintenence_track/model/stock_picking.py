from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class srikLotIngerit(models.Model):
    _inherit = 'stock.picking'

    len_warranty = fields.Integer('Warranty' ,compute='get_all_warranty')
    warranty_ids = fields.Many2many('maintenance.equipment' , string='Warranty IDS')

    @api.constrains('state')
    def create_warranty_records(self):
        print('In ?>>>>>>>>>>>')
        for rec in self:
            new_warranties = self.env['maintenance.equipment']
            sale_id = self.env['sale.order'].search([('name', '=', rec.origin)])
            if rec.state == 'done' and 'IN' not in rec.name:
                print('In ?>>>>>>>>>>>')
                for line in rec.move_ids_without_package:
                    print('Line >>>>>>>>>>> ' , line.product_id.id)
                    if line.product_id.product_tmpl_id.warranty == True:
                        move_lines = self.env['stock.move.line'].search([('move_id', '=', line.id)])
                        for move in move_lines:
                            for lot in line.lot_ids:
                                schedule_date = fields.Datetime.now()
                                schedule_date += relativedelta(**{f"{lot.repeat_unit}s": lot.repeat_every})
                                exsist_war = self.env['maintenance.equipment'].search([('lot_id' ,'=',lot.id)])
                                #
                                if exsist_war:
                                    pass
                                else:
                                    warranty = self.env['maintenance.equipment'].create({
                                        'product_id': line.product_id.id,
                                        'name' : line.product_id.name + ' - ' +rec.name,
                                        'lot_id': lot.id,
                                        'is_warranty': True ,
                                        'partner_id' : sale_id.partner_id.id,
                                        'warranty_start': move.start_warranty,
                                        'warranty_end': move.end_warranty,
                                        'reference' : sale_id.id,
                                        'maintenance_for1' : 'warranty',
                                        # 'maintenance_type' : 'preventive',
                                        # 'schedule_date' : schedule_date,
                                        # 'recurrent' : line.product_id.product_tmpl_id.recurrent
                                    })
                                print('warranty >>>>>> ' , warranty)
                                new_warranties += warranty
                rec.write({'warranty_ids': [(6, 0, new_warranties.ids)] })

            else:
                pass




    @api.depends('warranty_ids')
    def get_all_warranty(self):
        len_war = 0
        for rec in self:
            for i in rec.warranty_ids:

                len_war += 1

            rec.len_warranty = len_war

    #
    # def action_get_warranty(self):
    #     self.ensure_one()
    #
    #     res_ids = self.warranty_ids.ids
    #
    #     if len(res_ids) == 1:
    #         view_mode = 'form'
    #         view_id = self.env.ref('arados_maintenence_track.view_maintenance_request_form_custom1').id
    #     else:
    #         view_mode = 'tree'
    #         view_id = False
    #
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'maintenance.equipment',
    #         'view_mode': view_mode,
    #         'view_id': view_id,
    #         'res_id': res_ids if len(res_ids) > 1 else (res_ids and res_ids[0] or False),  # Select the first ID if multiple, else False
    #         'domain': [('id', 'in', res_ids)],
    #         'target': 'current',
    #     }


    def action_get_warranty(self):
        res_ids = self.warranty_ids.ids
        action = self.env['ir.actions.actions']._for_xml_id('arados_maintenence_track.action_assigned1')

        if len(res_ids) > 1:
            action['domain'] = [('id', 'in', res_ids)]
        elif len(res_ids) == 1:
            form_view = [(self.env.ref('arados_maintenence_track.view_maintenance_request_form_custom123').id, 'form')]

            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view

            action['res_id'] = res_ids[0]  # Set the single record ID here
        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action
