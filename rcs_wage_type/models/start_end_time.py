from odoo import models, fields


class StartEndTime(models.Model):
    _name = 'start.end.time'
    _description = 'Start End Time'
    _order = 'start_time'

    wage_type_id = fields.Many2one('wage.type', string='Wage Type')
    start_time = fields.Float(string='Start Time')
    end_time = fields.Float(string='End Time')
