RCS Wage Type
===================

.. contents:: Contents


Features
--------
The module serves as an interface between Lodas and Odoo.
Each attendance or absence is assigned to specific wage types.
These assignments can then be exported to a .txt file.

Users with the 'hr_attendance_manager' role can:
    * Create and edit wage types.
    * View and create exports.

Usage
-----
First, wage types need to be created in 'hr_employee' and holidays in 'resource.calendar.leaves'.
The distinction between high/low holiday is also set there.
In 'hr_leave', a wage type must be assigned to each respective absence.
When creating an attendance record, the assigned wage types will be visible under Details in the list view of attendances.
Absences are only visible in the export.

Field descriptions
------------------

**name**
    - Type: fields.Char
    - Description: Represents the name of the wage type. This field is required and provides a clear description of the type.

**number**
    - Type: fields.Integer
    - Description: The wage type ID. This field is required and is used for identification.
    - Default value: 0

**supplement**
    - Type: fields.Integer
    - Description: The percentage supplement applied to the wage type. This field is required.

**all_day**
    - Type: fields.Boolean
    - Description: Indicates whether the wage type applies to the entire day.
    - Default value: False

**start_before_midnight**
    - Type: fields.Boolean
    - Description: Determines whether the wage type applies if the start time is before midnight.
    - Default value: False

**standard_wage_type**
    - Type: fields.Boolean
    - Description: Indicates whether this is a standard wage type.
    - Default value: False

**time_ids**
    - Type: fields.One2many
    - Description: Links the start and end times (``start.end.time``) to this wage type. This allows defining specific time ranges.
    - Example for night supplement:
        - Row 1: 00:00 - 06:00
        - Row 2: 22:00 - 00:00
    - Times that go beyond midnight must be in individual lines

**weekday**
    - Type: fields.Selection
    - Description: Selection field for the weekday on which the wage type applies.
    - Options:
      - ``none``: No specific weekday.
      - ``0``: Monday
      - ``1``: Tuesday
      - ``2``: Wednesday
      - ``3``: Thursday
      - ``4``: Friday
      - ``5``: Saturday
      - ``6``: Sunday
    - Default value: none

**vacation_sick**
    - Type: fields.Selection
    - Description: Selection field to classify the type, specifying whether it applies to vacation or sick leave.
    - Options:
      - ``none``: Standard
      - ``vacation``: Vacation
      - ``sick``: Sick leave
    - Default value: none

**holiday_high**
    - Type: fields.Selection
    - Description: Indicates whether the wage type applies to major holidays.
    - Options:
      - ``no``: Not a holiday.
      - ``True``: Applies to major holidays.
      - ``False``: Applies to regular holidays.
    - Default value: no

Export
------
The menu items for export can be found in hr_attendance.
The export is generated as a .txt file, which can then also be found in a list view.
Each line of an export appears as follows:
1; check_in_date; 1; total_minutes; wage_type_id; employee_number; ;

Dependencies
------------
The module has dependencies on 'hr_holidays', 'hr_attendance' and 'resource'. 'hr_holidays_attendance' should be installed automatically.

Authors
-------

* RCS - Richter Computer Systemhaus GmbH (05.11.24)
    * nico_matuschek

