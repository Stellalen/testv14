import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class MrpOrder(models.Model):
    _inherit = 'mrp.production'

    instruction = fields.Text('Instructions')
    vendor_id = fields.Many2one('res.partner', string='Vendor')
