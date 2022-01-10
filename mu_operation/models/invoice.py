import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"
     
    incoterm_country_id = fields.Many2one('res.country','Incoterm Country')
    sgd_exchange_rate = fields.Float("SGD Exchange Rate")
    is_dropship = fields.Boolean('Dropship')


# class AccountMoveLine(models.Model):
#     _inherit = "account.move.line"
#
#     cust_po_no = fields.Char('Customer PO')
#     cust_po_item = fields.Char('PO item')
#     mpn = fields.Char('MPN')

