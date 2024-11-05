from odoo import models, fields, api


class HolidaysRequest(models.Model):
    _inherit = 'hr.leave'

    @api.model_create_multi
    def create(self, vals_list):
        for record in self:
            for vals in vals_list:
                if vals.get('state', '') == 'validate' and self.holiday_status_id.wage_type_id:
                    record._validate_leave()
        res = super(HolidaysRequest, self).create(vals_list)
        return res

    def write(self, vals):
        for record in self:
            if vals.get('state', '') == 'validate' and self.holiday_status_id.wage_type_id:
                record._validate_leave()
        res = super(HolidaysRequest, self).write(vals)
        return res

    def _validate_leave(self):
        recs = self.env['attendance_wage_type'].search([('leave_id', '=', self.id)])
        if recs:
            recs.unlink()

        self.env['attendance_wage_type'].create({
            'wage_type_id': self.holiday_status_id.wage_type_id.id,
            'time_from': self.date_from,
            'time_to': self.date_to,
            'hours': self.env['hr.employee'].search(
                [('resource_id', '=', self.employee_id.id)]).resource_calendar_id.hours_per_day * self.number_of_days,
            'leave_id': self.id,
        })


class HRLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    vacation_sick = fields.Selection([('none', 'Standard'), ('vacation', 'Vacation'), ('sick', 'Sick')], default="none")
    wage_type_id = fields.Many2one('wage.type')
