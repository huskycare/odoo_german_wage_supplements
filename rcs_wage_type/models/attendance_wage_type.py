from odoo import models, fields


class AttendanceWageType(models.Model):
    _name = 'attendance_wage_type'
    _description = 'Attendance Wage Type'
    _order = 'time_from'

    wage_type_id = fields.Many2one('wage.type', string='Wage Type')
    time_from = fields.Datetime('Time from')
    time_to = fields.Datetime('Time to')
    hours = fields.Float('Hours')
    attendance_id = fields.Many2one('hr.attendance', string='Attendance', ondelete='cascade')
    leave_id = fields.Many2one('hr.leave', string='Leave')
    export_id = fields.Many2one('export_hr_attendance', string='Export-ID')


    def write(self, vals):
        res = super(AttendanceWageType, self).write(vals)
        if 'export_id' in vals:
            self.attendance_id.compute_is_exported()
        return res
