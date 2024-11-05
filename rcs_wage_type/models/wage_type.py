from odoo import models, fields


class WageType(models.Model):
    _name = 'wage.type'
    _description = 'Wage Type'
    _order = 'supplement desc'

    name = fields.Char(string='Wage Type', required=True)
    number = fields.Integer(string='Wage Type Id', required=True)
    supplement = fields.Integer(string='Supplement in %', required=True)
    all_day = fields.Boolean(string='All Day', default=False)
    start_before_midnight = fields.Boolean(string='Check in Before Midnight', default=False)
    standard_wage_type = fields.Boolean(string='Standard Wage Type', default=False)
    time_ids = fields.One2many('start.end.time', 'wage_type_id', 'Times')
    weekday = fields.Selection([
        ('none', 'No Weekday'), ('0', 'Monday'), ('1', 'Tuesday'), ('2', 'Wednesday'), ('3', 'Thursday'),
        ('4', 'Friday'), ('5', 'Saturday'), ('6', 'Sunday')],
        string='Weekday', default='none')
    vacation_sick = fields.Selection([('none', 'Standard'), ('vacation', 'Vacation'), ('sick', 'Sick')], default="none")
    holiday_high = fields.Selection([('no', 'No Holidays'), ('True', 'True'), ('False', 'False')],
                                    string='Holiday High', default='no')
