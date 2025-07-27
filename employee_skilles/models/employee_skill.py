from odoo import models, fields, api
from odoo.exceptions import ValidationError



class EmployeeSkill(models.Model):
    _name = "employee.skill"
    _description = "Employee Skill"

    name = fields.Char(required=True)
    category = fields.Selection([
        ('technical', 'Technical'),
        ('soft', 'Soft'),
        ('language', 'Language'),
    ], required=True)
    description = fields.Text()


class EmployeeSkillLine(models.Model):
    _name = "employee.skill.line"
    _description = "Employee Skill Line"
    _rec_name = "skill_id"

    employee_id = fields.Many2one('hr.employee', required=True)
    skill_id = fields.Many2one('employee.skill', required=True)
    proficiency = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ], required=True)
    certification = fields.Binary()
    date_achieved = fields.Date()

    _sql_constraints = [
        ('employee_skill_unique', 'unique(employee_id, skill_id)', 'Duplicate skill for the employee is not allowed.')
    ]


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    skill_line_ids = fields.One2many('employee.skill.line', 'employee_id', string="Skills")
    skill_count = fields.Integer(compute="_compute_skill_count")

    @api.depends('skill_line_ids')
    def _compute_skill_count(self):
        for emp in self:
            emp.skill_count = len(emp.skill_line_ids)

    def action_open_skill_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'employee.skill.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_employee_id': self.id}
        }
class EmployeeSkillWizard(models.TransientModel):
    _name = 'employee.skill.wizard'
    _description = 'Wizard to Assign Skill to Employee'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    skill_id = fields.Many2one('employee.skill', string='Skill', required=True)
    proficiency = fields.Selection([
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ], string='Proficiency', required=True)
    certification = fields.Binary(string='Certification')
    date_achieved = fields.Date(string='Date Achieved')

    def action_assign_skill(self):
        """Create the employee.skill.line record if not duplicate."""
        self.ensure_one()

        existing = self.env['employee.skill.line'].search([
            ('employee_id', '=', self.employee_id.id),
            ('skill_id', '=', self.skill_id.id)
        ])
        if existing:
            raise ValidationError('This employee already has this skill.')

        self.env['employee.skill.line'].create({
            'employee_id': self.employee_id.id,
            'skill_id': self.skill_id.id,
            'proficiency': self.proficiency,
            'certification': self.certification,
            'date_achieved': self.date_achieved,
        })
