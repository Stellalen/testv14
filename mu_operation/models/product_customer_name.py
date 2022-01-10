from odoo import api, fields, models, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError


class ProductCustomerName(models.Model):
    _inherit = 'product.customer.name'

    product_code = fields.Char('Customer MPN')

