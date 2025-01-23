# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

# -*- coding: utf-8 -*-
{
    'name': 'RCS Wage Type',
    'version': '25.04.4',
    'category': 'RCS Models',
    'summary': '''Interface between Lodas and Odoo.
               Assignment of wage types to each attendance and absence.
               Export of each assigned wage type to a .txt file.''',
    'author': 'RCS - Richter Computer Systemhaus GmbH <matuschek.n>',
    'website': 'http://www.rcs.de',
    'images': [],
    'license': 'AGPL-3',
    'depends': [
        'hr_holidays',
        'hr_attendance',
        'resource',
        'datev_export',
    ],
    'data': [
        'views/wage_type.xml',
        'views/hr_attendance.xml',
        'views/export_hr_attendance.xml',
        'views/hr_leave.xml',
        'views/resource_calendar_leaves.xml',
        'security/ir.model.access.csv',
    ],
    'qweb': [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
