import time
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class StockRule(models.Model):
    _inherit = 'stock.rule'
    
    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, company_id, values):
        vals = super(StockRule, self)._get_stock_move_values(product_id, product_qty, product_uom, location_id, name, origin, company_id, values)
        description = vals.get('description_picking', '')
        if vals.get('sale_line_id', False):
            sale_line = self.env['sale.order.line'].browse(vals.get('sale_line_id'))
            if sale_line.cpn:
                description = f"Part Number: {sale_line.cpn}\n" + description
            if sale_line.mpn:
                description += f"\nMPN: {sale_line.mpn or ''}"
            if sale_line.order_id.client_order_ref:
                description += f"\nCustomer PO: {sale_line.order_id.client_order_ref}"
            if sale_line.cpo_line_no:
                description += f"\nPO Item: {sale_line.cpo_line_no}"
            if sale_line.coo_id:
                description += f"\nCountry of Origin: {sale_line.coo_id.name }"
            vals.update({'description_picking': description})
        return vals
        

class StockMove(models.Model):
    _inherit = "stock.move"

    ship_unit_value = fields.Float("Ship Unit Value")
    ship_line_total = fields.Float("Ship Line Total", compute='_amount_total')

    incoming_qty = fields.Float(related="product_id.incoming_qty", string="Incoming Qty", store=False, readonly=True)
    outgoing_qty = fields.Float(related="product_id.outgoing_qty", string="Outgoing Qty", store=False, readonly=True)
    qty_available = fields.Float(related="product_id.qty_available", string="Qty On Hand", store=False, readonly=True)
    qty_in_transit = fields.Float(related="product_id.qty_in_transit", string="Qty In Transit", store=False, readonly=True)

    @api.depends('ship_unit_value')
    def _amount_total(self):
        for rec in self:
            line_total = rec.ship_unit_value * rec.product_uom_qty
            rec.ship_line_total = line_total

    def action_show_product(self):
        self.ensure_one()
        prd_tmpl_id = self.product_id.product_tmpl_id
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'product.template',
            'views': [(False, 'form')],
            'target': 'current',
            'res_id': prd_tmpl_id.id
        }

    def action_show_picking(self):
        self.ensure_one()
        pick_id = self.picking_id
        action = {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.picking',
            'views': [(False, 'form')],
            'target': 'current',
            'res_id': pick_id.id
        }
        return action


class StockPicking(models.Model):
    _inherit = "stock.picking"

    ship_total = fields.Float("Ship Total", compute='_compute_total')
    reference = fields.Char("Partner Reference")

    @api.depends('move_ids_without_package.ship_line_total')
    def _compute_total(self):
        for order in self:
            total_lst = order.move_ids_without_package.mapped('ship_line_total')
            total = len(total_lst) > 0 and sum(total_lst) or 0.0
            order.ship_total = total

class QualityCheck(models.Model):
    _inherit = 'quality.check'

    reference = fields.Char(related="picking_id.reference", string="Reference", store=True)


