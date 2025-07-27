from odoo import models, fields, api

AVAILABLE_TIMELINE = [
    ('1', 'Normal'),
    ('2', 'Urgent'),
    ('3', 'Top Urgent'),
]


class CrmStageInherited(models.Model):
    _inherit = 'crm.stage'
    is_lost = fields.Boolean(default=False, string='Is Lost Stage')
    is_negotiation = fields.Boolean(default=False, string='Is Negotiation Stage')


class CrmLeadInherited(models.Model):
    _inherit = 'crm.lead'

    customer_logo = fields.Binary( string='LOGO')
    source_lang_selection = fields.Selection(
        selection=lambda self: [(str(lang.id), lang.name) for lang in self.env['res.lang'].search(['|', ('active', '=', False), ('active', '=', True)])],
        string='Source Lang',
        widget='selection'
    )
    target_lang_selection = fields.Selection(
        selection=lambda self: [(str(lang.id), lang.name) for lang in self.env['res.lang'].search(['|', ('active', '=', False), ('active', '=', True)])],
        string='Target Lang',
        widget='selection'
    )
    client_type = fields.Selection(
        [('1', 'Individual'), ('2', 'Company')], string="Client Type" , default = '2')
    company_name = fields.Char('Company Name')
    Company_sector = fields.Selection(
        [('1', 'Academic'), ('2', 'Energy') , ('3', 'Fashion'), ('4', 'Financial'), ('5', 'Government'), ('6', 'Healthcare'), ('7', 'Legal'), ('8', 'Manufacturing'), ('9', 'Media'), ('10', 'NGOs'), ('11', 'Property'), ('12', 'Retail'), ('13', 'Technology'), ('14', 'Tourism'), ('15', 'Other ')], string='Company Sector' , default = '15')
    contact_name = fields.Char('Contact Name')
    email_address = fields.Char('Email Address')
    phone = fields.Char('Phone Number')
    service_type = fields.Selection(
        [('1', 'Written'), ('2', 'Interpretation')], string="Client Type" , default = '1')
    Written_option = fields.Selection(
        [('1', 'Translation '), ('2', 'Localization'), ('3', 'Copywriting'), ('4', 'Editing & Proofreading'), ('5', 'Subtitling'), ('6', 'Transcription')], string="Options" , default = '1')
    Interpretation_option = fields.Selection(
        [('1', 'Simultaneous'), ('2', 'Consecutive')], string="Options" , default = '1')
    delivery_type = fields.Selection(
        [('1', 'Soft Copy'), ('2', 'Hard Copy')], string="Delivery Type" , default = '1')
    service_industry = fields.Selection(
        [('1', 'Academic'), ('2', 'Commercial') , ('3', 'General '), ('4', 'Legal'), ('5', 'Literary'), ('6', 'Marketing'), ('7', 'Medical'), ('8', 'Technical'), ('9', 'Other')], string='Service Industry' , default = '3')


    priority_work = fields.Selection(
        [('1', 'Normal'), ('2', 'Urgent'), ('3', 'Top Urgent')], string="Priority" , default = '1')

    deadline = fields.Date('Deadline')
    gender = fields.Selection(
        [('1', 'Male'), ('2', 'Female')], string="Gender" , default = '1')
    lang = fields.Many2one('res.lang', string='Langauge')
    service_ids = fields.One2many('crm.service.line', 'crm_id', string='Service')
    my_description = fields.Text('')
    payment_terms = fields.Selection(
        [('1', 'Advance Payment'), ('2', 'Partial Payment'), ('3', 'Progress Payments'), ('3', 'Progress Payments'), ('4', 'Prepaid'), ('5', 'Cash on Delivery'), ('6', 'Net 30') , ('7', 'Installments')], string="Payment Terms" , default = '1')
    is_interpretation = fields.Boolean(string='Is Interpretation')
    # common fields
    detailed_timeline = fields.Datetime(string='Detailed Timeline')

    timeline = fields.Selection(AVAILABLE_TIMELINE
                                , string='Timeline', index=True,
                                default=AVAILABLE_TIMELINE[0][0], required=True)
    partner_company_type = fields.Char(compute='_compute_partner_company_type', string='Customer Type'
                                       , readonly=True, store=True)

    # interpretation fields
    interpretation_type = fields.Selection([('0', 'Simultaneous'), ('1', 'Consecutive')],
                                           string="Interpretation Type")
    requirements = fields.Selection([('0', 'Booth'), ('1', 'Headset')],
                                    string="others")
    event_name = fields.Char(string='Event Name')
    event_location = fields.Char(string='Event Location')
    days_number = fields.Integer(string='Number of Days')
    event_duration = fields.Integer(string='Event Duration')
    event_date = fields.Datetime(string='Event Date')
    attendees_number = fields.Integer(string='Attendees Number')
    discussed_topics = fields.Text(string='Topics to be Discussed')
    is_broadcasting_needed = fields.Boolean(string='Broadcasting Needed')
    hotel_ballroom_number = fields.Integer(string='Hotel Ballroom Number')
    required_interpreters_number = fields.Integer(string='Required Interpreters Number')
    technicians_number = fields.Integer(string='Technicians Number')

    # interpreter_lines = fields.One2many('interpreter.line', 'lead_id', string='Interpreters')
    interpreter_counts = fields.Integer(readonly='1', compute='_compute_interpreter_count')

    additional_devices = fields.Char(string='Additional devices')
    source = fields.Many2many('ir.attachment', string='Source Attachment')
    is_lost_stage = fields.Boolean(compute="_compute_is_lost_stage")
    is_nego = fields.Boolean()
    is_quotation = fields.Boolean()
    order_id = fields.Many2one('sale.order' , string='Quotation')
    len_order_id = fields.Integer( compute="_1235888")
    service_id = fields.Many2one('product.product' , string='Service', domain="[('detailed_type','=', 'service')]")
    text_for_kanban = fields.Text('Text' ,compute="get_text_for_kanban" , store=True)


    @api.constrains('service_id', 'source_lang_selection', 'target_lang_selection')
    def get_text_for_kanban(self):
        for line in self:
            text = ''
            if line.service_id and line.source_lang_selection and line.target_lang_selection:
                service_name = line.service_id.name
                source_lang_name = self.env['res.lang'].browse(int(line.source_lang_selection)).name
                target_lang_name = self.env['res.lang'].browse(int(line.target_lang_selection)).name

                text = f"{source_lang_name} - {target_lang_name}"

            line.text_for_kanban = text

    @api.constrains('source')
    def create_lines(self):
        if self.source:
            print('self.source  >>>>>> ' , self.source)
            last = self.env["crm.service.line"].search([('crm_id' ,'=',self.id)])
            last.unlink()
            for rec in self.source:
                print('int(self.source_lang_selection) >>>>> ' , int(self.source_lang_selection))
                print('int(self.source_lang_selection) >>>>> ' , int(self.target_lang_selection))

                create_line = self.env["crm.service.line"].create({
                    'crm_id' :self.id,
                    'source' :rec,
                    'source_lang' :int(self.source_lang_selection),
                    'target_lang' :int(self.target_lang_selection)
                })

    @api.depends('order_id')
    def _1235888(self):
        for lead in self:
            if lead.order_id:
                lead.len_order_id =1
            else:
                lead.len_order_id =0
    def action_open_sale_order(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Sale Order',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.order_id.id,
            'target': 'current',
        }

    def create_quotation(self):
        for rec in self:
            partner = self.env['res.partner'].create({
            'name' : rec.name,
                'is_company' : True if rec.client_type == '2' else False,
                'email' : rec.email_address,
                'phone' : rec.phone
            })
            quot = self.env['sale.order'].create({
            'partner_id' : partner.id,
                'opportunity_id' : rec.id,
                'commitment_date':rec.deadline
            })
            for line in rec.service_ids:
                s_o_line = self.env['sale.order.line'].create({
                    'order_id': quot.id,
                    'product_id': line.service_id.id,
                    'name': line.service_id.name,
                    'product_uom_qty': 1,
                    'source_language' :  line.source_lang.id,
                    'target_language' : line.target_lang.id,
                    'estimated_number_of_pages' : line.pages,
                    'estimated_number_of_words' : line.words,
                    'source_attachment_ids' : line.source,
                    'tax_id' : line.vat,
                    'price_unit' : line.Rate,
                    'discount' : line.disc,
                    'crm_line_id' : line.id
                })
                line.sale_line_id = s_o_line.id
            rec.is_quotation = True
            rec.order_id = quot.id


    def action_accept(self):
        negotiation_stage = self.env['crm.stage'].search([('name', '=', 'Negotiation')], limit=1)
        if negotiation_stage:
            for record in self:
                record.write({'stage_id': negotiation_stage.id , 'is_nego' : True, 'active': True})
            # Perform any other actions related to accepting the record
        else:
            # Handle the case where the 'Negotiation' stage is not found
            pass

    def action_reject(self):
        for record in self:
            record.active = False
            # Perform any other actions related to rejecting the record
    @api.depends('stage_id')
    def _compute_is_lost_stage(self):
        for lead in self:
            lost_stage = self._stage_find(domain=[('is_lost', '=', True)], limit=None)
            print(lost_stage)
            if lead.stage_id == lost_stage:
                lead.is_lost_stage = True
            else:
                lead.is_lost_stage = False

    @api.depends('partner_id.company_type')
    def _compute_partner_company_type(self):
        for lead in self:
            if lead.partner_id.company_type:
                lead.partner_company_type = 'Individual' if lead.partner_id.company_type == 'person' else 'Company'

    # @api.depends('interpreter_lines')
    # def _compute_interpreter_count(self):
    #     for lead in self:
    #         lead.interpreter_counts = self.env['interpreter.line'].search_count([('lead_id', '=', lead.id)])
    #
    # def action_set_lost(self, **additional_values):
    #     res = super(CrmLeadInherited, self).action_set_lost(**additional_values)
    #
    #     for lead in self:
    #         lost_stage = self._stage_find(domain=[('is_lost', '=', True)], limit=None)
    #
    #         if lost_stage:
    #             lead.write({'stage_id': lost_stage.id, 'active': True})
    #
    #     return res
class CRMServiceLine(models.Model):
    _name = "crm.service.line"

    crm_id = fields.Many2one('crm.lead')
    service_id = fields.Many2one('product.product' , string='Service', domain="[('detailed_type','=', 'service')]")
    source = fields.Many2many('ir.attachment', 'sale_line_source_attachment_rel125', string='Source')
    source_lang =fields.Many2one('res.lang' , string='Source' ,domain="['|',('active', '=', False),('active', '=', True)  ]")
    target_lang =fields.Many2one('res.lang' , string='Target' , domain="['|',('active', '=', False),('active', '=', True)  ]")
    words = fields.Integer('Words')
    pages = fields.Integer('Pages')
    Rate = fields.Integer('Rate')
    vat = fields.Many2one('account.tax','VAT')
    disc = fields.Integer('Disc %')
    total = fields.Float('Total' ,compute="calculate_total")
    sale_line_id = fields.Many2one('sale.order.line')
    display_text = fields.Text(string='Display Text', compute='_compute_display_text')

    @api.constrains('service_id', 'source_lang', 'target_lang', 'words', 'pages', 'Rate', 'vat', 'disc')
    def change_values(self):
        for rec in self:
            if rec.sale_line_id and not rec._context.get('skip_change_values'):
                tax_ids = [(6, 0, [rec.vat.id])]
                rec.sale_line_id.with_context(skip_change_values=True).write({
                    'product_id': rec.service_id.id,
                    'estimated_number_of_pages': rec.pages,
                    'estimated_number_of_words': rec.words,
                    'source_language': rec.source_lang.id,
                    'target_language': rec.target_lang.id,
                    'price_unit': rec.Rate,
                    'tax_id': tax_ids,
                    'discount': rec.disc
                })

    @api.depends('service_id', 'source_lang', 'target_lang' , 'target_lang')
    def _compute_display_text(self):
        for rec in self:
            display_text = ''
            if rec.service_id and rec.source_lang and rec.target_lang:
                display_text += rec.service_id.name + '\n'
                display_text += rec.source_lang.name + '-' + rec.target_lang.name + '\n'
            rec.display_text = display_text

    @api.depends('Rate', 'vat', 'disc')
    def calculate_total(self):
        for rec in self:
            if rec.Rate:
                total = rec.Rate
                if rec.vat:
                    total += (rec.Rate * rec.vat.amount / 100)
                if rec.disc:
                    if rec.vat :
                        total -= (total * rec.disc / 100)
                    else:
                        total -= (rec.Rate * rec.disc / 100)
                rec.total = total
            else:
                rec.total = 0.0  # If Rate is not provided, total will be 0.0

class InterpreterLine(models.Model):
    _name = "interpreter.line"
    _description = "Interpreters"
    interpreter_name = fields.Many2one('hr.employee', string="Interpreter", required='1')
    rate = fields.Float(string="Rate")
    lead_id = fields.Many2one('crm.lead')
