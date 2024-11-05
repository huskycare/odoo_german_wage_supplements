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

