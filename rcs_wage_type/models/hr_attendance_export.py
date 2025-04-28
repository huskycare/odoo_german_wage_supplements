import base64
import io
import odoo
from datetime import datetime
from odoo import models, fields
from odoo.exceptions import UserError


class HrAttendanceExport(models.Model):
    _name = 'export.hr.attendance'
    _description = 'Export for HR Attendance Export'
    _rec_name = 'filename'

    export_file = fields.Binary(string='Export File')
    filename = fields.Char(string='Filename')
    attendance_ids = fields.One2many('attendance_wage_type', 'export_id', string="Attendance IDs")
    date_from = fields.Date(string='Date From')
    date_to = fields.Date(string='Date To')

    def get_export_values(self, export_file=None):
        self.ensure_one()
        empty = self.env['export.hr.attendance'].search([('filename', '=', False), ('id', '!=', self.id)])
        empty.unlink()

        date_from_adjusted = self.date_from.replace(day=1)

        records = self.env['attendance_wage_type'].search([
            ('export_id', '=', False),
            ('time_from', '>=', self.date_from),
            ('time_from', '<=', self.date_to)
        ])

        summarized_data = {}
        for record in records:
            employee_id = (record.attendance_id.employee_id.barcode if record.attendance_id.employee_id
                           else record.leave_id.employee_id.barcode) or 'UNKNOWN'
            wage_type_key = record.wage_type_id.number if record.wage_type_id else 'UNKNOWN'
            key = (employee_id, wage_type_key)

            if key not in summarized_data:
                summarized_data[key] = 0
            summarized_data[key] += record.hours * 60
            record.write({'export_id': self.id})

        export_content = io.StringIO()
        datev_consultant_number = self.env.user.company_id.datev_consultant_number or ''
        datev_client_number = self.env.user.company_id.datev_client_number or ''

        export_content.write(f"""[Allgemein]
Ziel=LODAS
Version_SST=1.0
Version_DB=11.1
BeraterNr={datev_consultant_number}
MandantenNr={datev_client_number}
Datumsformat=TT/MM/JJJJ
Stringbegrenzer="


[Satzbeschreibung]
1;u_lod_bwd_buchung_standard;abrechnung_zeitraum#bwd;bs_nr#bwd;bs_wert_butab#bwd;la_eigene#bwd;pnr#bwd;kostenstelle#bwd;


[Bewegungsdaten]
""")

        for (employee_id, wage_type), total_minutes in summarized_data.items():
            line = f"1;{date_from_adjusted.strftime('%d/%m/%Y')};1;{int(round(total_minutes, 0))};{wage_type};{employee_id};;"
            export_content.write(line + "\n")

        if summarized_data:
            self.write({
                'export_file': base64.b64encode(
                    export_content.getvalue().encode(encoding='iso-8859-1', errors="replace")),
                'filename': "export_" + str(
                    odoo.fields.Datetime.context_timestamp(self, datetime.now()).strftime('%Y_%m_%d_%H_%M')).replace(
                    '-', '_') + ".txt",
            })
        else:
            raise UserError("There are no records to export.")

        return {
            'name': 'Export',
            'view_mode': 'form',
            'view_id': self.env.ref('rcs_wage_type.hr_attendance_export_view').id,
            'res_model': 'export.hr.attendance',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }
