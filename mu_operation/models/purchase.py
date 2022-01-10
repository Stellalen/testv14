from odoo import api, fields, models

class PurchaseOrder(models.Model):
    _inherit="purchase.order"
    
    def action_rfq_send(self):
        res = super(PurchaseOrder, self).action_rfq_send()
        res['context']['custom_layout'] = 'mu_operation.mail_notification_paynow_purchase'
        return res
    
# class PurchaseOrderLine(models.Model):
#     _inherit = 'purchase.order.line'
#
#     coo_id = fields.Many2one('res.country', 'Country of origin')
#     qty_remaining = fields.Float('Remaining Quantity', copy=False, compute='_compute_qty_remaining',  compute_sudo=True, store=True, digits='Product Unit of Measure', default=0.0)
#
#
#     @api.depends('qty_received', 'product_qty')
#     def _compute_qty_remaining(self):
#         for line in self:
#             line.qty_remaining = line.product_qty -  line.qty_received
#
#
#     def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
#         vals = super(PurchaseOrderLine, self)._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
#         vals.update({'coo_id':self.coo_id and self.coo_id.id or False})
#         return vals
#
#     def _get_product_purchase_description(self, product_lang, seller=False):
#         self.ensure_one()
#         name = seller and seller.product_name or product_lang.name
#         if product_lang.description_purchase:
#             name += '\n' + product_lang.description_purchase
#         return name
#
#     @api.onchange('product_qty', 'product_uom')
#     def _onchange_quantity(self):
#         super(PurchaseOrderLine, self)._onchange_quantity()
#
#         if not self.product_id:
#             return
#         params = {'order_id': self.order_id}
#         seller = self.product_id._select_seller(
#             partner_id=self.partner_id,
#             quantity=self.product_qty,
#             date=self.order_id.date_order and self.order_id.date_order.date(),
#             uom_id=self.product_uom,
#             params=params)
#
#         if not seller or not self.price_unit:
#             self.price_unit = 999.00