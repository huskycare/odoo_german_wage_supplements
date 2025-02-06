from odoo import models, fields, api
import pytz
import calendar
from odoo.fields import Datetime


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    attendance_ids = fields.One2many('attendance_wage_type', 'attendance_id', string='Attendance Wage Type')
    total_hours = fields.Float('Total Hours', compute='_compute_total_hours', store=True)
    is_exported = fields.Boolean('Is Exported', compute='compute_is_exported', store=True)
    holiday = fields.Many2one('resource.calendar.leaves', string='Holiday')

    @api.depends('attendance_ids')
    def _compute_total_hours(self):
        for record in self:
            record.total_hours = 0
            for attendance in record.attendance_ids:
                record.total_hours += attendance.hours

    @api.depends('check_in', 'check_out')
    def compute_is_exported(self):
        for attendance in self.attendance_ids:
            if attendance.export_id:
                self.is_exported = True
            else:
                self.is_exported = False

    @api.model_create_multi
    def create(self, vals_list):
        res = super(HrAttendance, self).create(vals_list)
        res.create_attendance_wage_type()
        return res

    def write(self, vals):
        res = super(HrAttendance, self).write(vals)
        if 'is_exported' not in vals and 'holiday' not in vals:
            self.create_attendance_wage_type()
        return res

    def create_attendance_wage_type(self):
        for record in self:
            if record.check_in and record.check_out:
                wage_type_ids = record.env['wage.type'].search([], order='supplement desc')
                attendance_wage_type_list = []
                check_in = Datetime.context_timestamp(record, record.check_in).replace(second=0, microsecond=0)
                check_out = Datetime.context_timestamp(record, record.check_out).replace(second=0, microsecond=0)
                list_work_time = [(check_in, check_out)]

                for wage_type_id in wage_type_ids:
                    record.holiday = False
                    if wage_type_id.holiday_high == 'no':
                        holidays = []
                    else:
                        holidays = self.env['resource.calendar.leaves'].search(
                            [
                                '&',
                                ('resource_id', '=', None),
                                ('holiday_high', '=', wage_type_id.holiday_high == 'True')
                            ]
                        )

                    if check_in.date() == check_out.date():
                        date = check_in.date()
                        if wage_type_id.start_before_midnight and record._check_before_midnight(check_in):
                            attendance_list, list_work_time = record._check_times(list_work_time, wage_type_id,
                                                                                  attendance_wage_type_list, date)
                            if not len(attendance_list) == len(attendance_wage_type_list):
                                attendance_wage_type_list.append(attendance_list)
                        if wage_type_id.all_day:
                            if int(wage_type_id.weekday) == date.weekday():
                                attendance_wage_type_list.append(
                                    record._data_for_append(wage_type_id, check_in, check_out,
                                                            round((check_out - check_in).total_seconds() / 3600, 2)))
                                break

                        elif record._check_hollidays(date, holidays):
                            attendance_list, list_work_time = record._check_times(list_work_time, wage_type_id,
                                                                                  attendance_wage_type_list, date)
                            if not len(attendance_list) == len(attendance_wage_type_list):
                                attendance_wage_type_list.append(attendance_list)

                        elif not holidays and not record._check_hollidays(
                                                                          date, holidays) and not wage_type_id.standard_wage_type and not wage_type_id.start_before_midnight:
                            attendance_list, list_work_time = record._check_times(list_work_time, wage_type_id,
                                                                                  attendance_wage_type_list, date)
                            if not len(attendance_list) == len(attendance_wage_type_list):
                                attendance_wage_type_list.append(attendance_list)

                    elif not wage_type_id.standard_wage_type and not wage_type_id.start_before_midnight:
                        if holidays and not record._check_hollidays(check_in.date(), holidays):
                            continue
                        attendance_list, list_work_time = record._check_times(list_work_time, wage_type_id,
                                                                              attendance_wage_type_list,
                                                                              check_in.date())
                        if not len(attendance_list) == len(attendance_wage_type_list):
                            attendance_wage_type_list.append(attendance_list)

                        if holidays and not record._check_hollidays(check_out.date(), holidays):
                            continue
                        attendance_list, list_work_time = record._check_times(list_work_time, wage_type_id,
                                                                              attendance_wage_type_list,
                                                                              check_out.date())
                        if not len(attendance_list) == len(attendance_wage_type_list):
                            attendance_wage_type_list.append(attendance_list)

                    elif wage_type_id.start_before_midnight:
                        attendance_list, list_work_time = record._check_times(list_work_time, wage_type_id,
                                                                              attendance_wage_type_list,
                                                                              check_out.date())
                        if not len(attendance_list) == len(attendance_wage_type_list):
                            attendance_wage_type_list.append(attendance_list)

                    if wage_type_id.standard_wage_type:
                        if len(list_work_time) == 0:
                            break
                        else:
                            for i in range(len(list_work_time)):
                                pair = list_work_time[i]
                                check_in = pair[0]
                                check_out = pair[1]
                                attendance_wage_type_list.append(
                                    record._data_for_append(wage_type_id, check_in, check_out,
                                                            round(
                                                                (check_out - check_in).total_seconds() / 3600,
                                                                2)))

                records = self.env['attendance_wage_type'].search([('attendance_id', '=', self.id)])
                if records:
                    records.unlink()
                attendance_wage_type_list = [element for element in attendance_wage_type_list if element is not None]
                self.env['attendance_wage_type'].create(attendance_wage_type_list)

    def _data_for_append(self, data, time_from, time_to, hours):
        if hours > 0:
            return {
                'wage_type_id': data.id,
                'time_from': pytz.timezone(self.env.context['tz']).localize(
                    Datetime.from_string(time_from.replace(tzinfo=None)), is_dst=None).astimezone(pytz.utc).replace(
                    tzinfo=None),
                'time_to': pytz.timezone(self.env.context['tz']).localize(
                    Datetime.from_string(time_to.replace(tzinfo=None)), is_dst=None).astimezone(pytz.utc).replace(
                    tzinfo=None),
                'hours': hours,
                'attendance_id': self.id,
            }

    def _check_hollidays(self, date, holidays):
        for holiday in holidays:
            if date == Datetime.context_timestamp(self, holiday.date_from).date():
                self.holiday = holiday
                return True
        return False

    def open_hr_attendance_wage_types(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Hr Attendance Wage type',
            'view_mode': 'form',
            'res_model': 'hr.attendance',
            'view_id': self.env.ref('rcs_wage_type.rcs_view_hr_attendance_wage_type_form').id,
            'target': 'current',
            'res_id': self.id
        }

    def _check_times(self, list_work_time, wage_type_id, attendance_wage_type_list, date):
        for i in range(len(list_work_time)):
            if len(list_work_time) == 0 and len(list_work_time) < i:
                break
            pair = list_work_time[0]
            check_in = pair[0]
            check_out = pair[1]

            if wage_type_id.all_day and len(wage_type_id.time_ids) <= 0:
                midnight = check_out.replace(hour=0, minute=0, second=0, microsecond=0)

                if int(wage_type_id.weekday) == check_in.weekday():
                    attendance_wage_type_list.append(
                        self._data_for_append(wage_type_id, check_in, midnight,
                                              round((midnight - check_in).total_seconds() / 3600, 2)))
                    list_work_time.pop(0)
                    if not midnight >= check_out:
                        list_work_time.append((midnight, check_out))

                if int(wage_type_id.weekday) == check_out.weekday():
                    attendance_wage_type_list.append(
                        self._data_for_append(wage_type_id, midnight, check_out,
                                              round((check_out - midnight).total_seconds() / 3600, 2)))
                    list_work_time.pop(0)
                    if not check_in >= midnight:
                        list_work_time.append((check_in, midnight))
                continue

            for time_id in wage_type_id.time_ids:
                if self.holiday:
                    day_start_time = Datetime.context_timestamp(self, self.holiday.date_from)
                    day_end_time = Datetime.context_timestamp(self, self.holiday.date_to)
                    if time_id.end_time >= 23.98:
                        if check_out.month != check_in.month:
                            day_end_time = day_end_time.replace(month=day_end_time.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
                        elif check_out.day != check_in.day:
                            day_end_time = day_end_time.replace(day=day_end_time.day + 1, hour=0, minute=0, second=0,
                                                            microsecond=0)
                else:
                    start_hour = int(time_id.start_time)
                    start_minutes = int((time_id.start_time - start_hour) * 60)
                    day_start_time = check_in.replace(year=date.year, month=date.month, day=date.day, hour=start_hour,
                                                      minute=start_minutes, second=0, microsecond=0)

                    end_hour = int(time_id.end_time)
                    end_minutes = int((time_id.end_time - end_hour) * 60)
                    day_end_time = check_out.replace(year=date.year, month=date.month, day=date.day, hour=0, minute=0, second=0, microsecond=0)
                    if end_hour == 0 and end_minutes == 0 or time_id.end_time >= 23.98:
                        last_day_of_month = calendar.monthrange(day_end_time.year, day_end_time.month)[1]
                        if day_end_time.day == last_day_of_month:
                            day_end_time = day_end_time.replace(month= day_end_time.month + 1, day=1)
                        else:
                            day_end_time = day_end_time.replace(day=date.day + 1)
                    else:
                        day_end_time = day_end_time.replace(hour=end_hour, minute=end_minutes)
                if day_end_time <= check_in or day_start_time >= check_out:
                    list_work_time.pop(0)
                    list_work_time.append((check_in, check_out))
                    continue
                elif day_start_time <= check_in:
                    if day_end_time <= check_out:
                        attendance_wage_type_list.append(
                            self._data_for_append(wage_type_id, check_in, day_end_time,
                                                  round(
                                                      (day_end_time - check_in).total_seconds() / 3600,
                                                      2)))
                        list_work_time.pop(0)
                        if day_end_time == check_out:
                            continue
                        check_in = day_end_time
                        list_work_time.append((day_end_time, check_out))
                        continue
                    elif day_end_time >= check_out:
                        attendance_wage_type_list.append(
                            self._data_for_append(wage_type_id, check_in, check_out,
                                                  round(
                                                      (check_out - check_in).total_seconds() / 3600,
                                                      2)))
                        list_work_time.pop(0)
                        return attendance_wage_type_list, list_work_time

                elif day_start_time >= check_in:
                    if day_end_time <= check_out:
                        attendance_wage_type_list.append(
                            self._data_for_append(wage_type_id, day_start_time, day_end_time,
                                                  round(
                                                      (day_end_time - day_start_time).total_seconds() / 3600,
                                                      2)))
                        if day_end_time == check_out and day_start_time == check_in:
                            list_work_time.pop(0)
                            return attendance_wage_type_list, list_work_time
                        if not day_start_time == check_in:
                            list_work_time.append((check_in, day_start_time))
                        if not day_end_time == check_out:
                            list_work_time.append((day_end_time, check_out))
                        list_work_time.pop(0)
                        continue
                    elif day_start_time <= check_in:
                        list_work_time.pop(0)
                        list_work_time.append((check_in, check_out))
                        continue
                    elif day_end_time >= check_out:
                        attendance_wage_type_list.append(
                            self._data_for_append(wage_type_id, day_start_time, check_out,
                                                  round(
                                                      (check_out - day_start_time).total_seconds() / 3600,
                                                      2)))
                        if day_end_time == check_out and day_start_time == check_in:
                            list_work_time.pop(0)
                            return attendance_wage_type_list, list_work_time
                        if not day_start_time == check_in:
                            list_work_time.pop(0)
                            list_work_time.append((check_in, day_start_time))
                        continue
                else:
                    list_work_time.pop(0)
                    list_work_time.append((check_in, check_out))
        return attendance_wage_type_list, list_work_time

    def _check_before_midnight(self, check_in):
        hr_attendance = self.env['hr.attendance'].search(
            [('employee_id', '=', self.employee_id.id), ('id', 'not in', self.ids)], limit=1, order='check_out desc')
        if hr_attendance:
            seconds = (check_in - Datetime.context_timestamp(self, hr_attendance.check_out)).total_seconds()
            return True if 7200 > seconds > 0 else False
        else:
            return False
