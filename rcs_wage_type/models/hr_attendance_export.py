import base64

from odoo import models, fields
import io
import odoo
from datetime import datetime


class HrAttendanceExport(models.Model):
    _name = 'export_hr_attendance'
    _description = 'Export for HR Attendance Export'
    _rec_name = 'filename'

    export_file = fields.Binary(string='Export File')
    filename = fields.Char(string='Filename')
    attendance_ids = fields.One2many('attendance_wage_type', 'export_id', string="Attendance IDs")

    def get_export_values(self, export_file=None):
        self.ensure_one()
        empty = self.env['export_hr_attendance'].search([('filename', '=', False), ('id', '!=', self.id)])

        empty.unlink()

        records = self.env['attendance_wage_type'].search([('export_id', '=', False)])

        export_content = io.StringIO()

        for record in records:
            u_lod_bwd_buchung_standard = 1
            abrechnung_zeitraum_bwd = record.time_from.strftime('%d/%m/%Y') if record.time_from else ''
            bs_nr_bwd = 1
            bs_wert_butab_bwd = int(record.hours * 60)
            la_eigene_bwd = record.wage_type_id.number if record.wage_type_id else ''
            pnr_bwd = record.attendance_id.employee_id.id if record.attendance_id.employee_id else record.leave_id.employee_id.id
            kostenstelle_bwd = ''

            line = f"{u_lod_bwd_buchung_standard};{abrechnung_zeitraum_bwd};{bs_nr_bwd};{bs_wert_butab_bwd};{la_eigene_bwd};{pnr_bwd};{kostenstelle_bwd};\n"
            export_content.write(line)
            record.write({'export_id': self.id})
        if records:
            self.write(
                {'export_file': base64.b64encode(
                    export_content.getvalue().encode(encoding='iso-8859-1', errors="replace")),
                 'filename': "export_" + str(
                     odoo.fields.Datetime.context_timestamp(self, datetime.now()).strftime('%Y_%m_%d_%H_%M')).replace(
                     '-', '_') + ".txt",
                 })

        return {
            'name': 'Export',
            'view_mode': 'form',
            'view_id': self.env.ref('rcs_wage_type.hr_attendance_export_view').id,
            'res_model': 'export_hr_attendance',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }
