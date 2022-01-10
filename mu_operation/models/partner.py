from odoo import api, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    delivery_status_count = fields.Integer(compute='_compute_delivery_status_count', string='delivery status Count')
    grn_status_count = fields.Integer(compute='_compute_grn_status_count', string='GRN Status Count')

    def _compute_delivery_status_count(self):
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])

        stock_move_groups = self.env['stock.move'].read_group(
            domain=[('partner_id', 'in', all_partners.ids),('picking_type_id.code', '=', 'outgoing'),('state', 'in', ('waiting', 'assigned','confirmed','partially_available'))],
            fields=['partner_id'], groupby=['partner_id']
        )
        partners = self.browse()
        for group in stock_move_groups:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.delivery_status_count += group['partner_id_count']
                    partners |= partner
                partner = partner.parent_id
        (self - partners).delivery_status_count = 0

    def _compute_grn_status_count(self):
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])

        stock_picking_groups = self.env['stock.picking'].read_group(
            domain=[('partner_id', 'in', all_partners.ids), ('picking_type_id.code', '=', 'incoming'), ('state', 'in', ('assigned',))],
            fields=['partner_id'], groupby=['partner_id']
        )
        partners = self.browse()
        for group in stock_picking_groups:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.grn_status_count += group['partner_id_count']
                    partners |= partner
                partner = partner.parent_id
        (self - partners).grn_status_count = 0

    def get_delivery_status(self):
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        move_ids = self.env['stock.move'].search([('partner_id', 'in', all_partners.ids),
                                                  ('picking_type_id.code', '=', 'outgoing'),
                                                  ('state', 'in', ('waiting', 'assigned', 'confirmed', 'partially_available'))])
        action = {
            'name': _('Delivery Status'),
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'res_model': 'stock.move',
            'context': {'tree_view_ref':'mu_operation.view_stock_move_forecast_delivery_tree'},
            'domain': [('id', 'in', move_ids.ids)],
        }
        return action
        
    def get_grn_status(self):
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        picking_ids = self.env['stock.picking'].search([('partner_id', 'in', all_partners.ids),
                                                  ('picking_type_id.code', '=', 'incoming'),
                                                  ('state', 'in', ('assigned',))])
        result = self.env["ir.actions.actions"]._for_xml_id('stock.action_picking_tree_all')
        result['domain'] = "[('id','in',%s)]" % (picking_ids.ids)
        return result
