from odoo import models, fields


class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'

    holiday_high = fields.Boolean(string='Holiday High', default=False)
