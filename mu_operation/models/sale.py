from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    incoterm_country_id = fields.Many2one('res.country', 'Incoterm Country')
    client_order_ref = fields.Char(string='Customer PO', copy=False)

    def _prepare_invoice(self):
        vals = super(SaleOrder, self)._prepare_invoice()
        vals.update({'incoterm_country_id': self.incoterm_country_id and self.incoterm_country_id.id or False})
        return vals

    @api.onchange('pricelist_id')
    def _onchange_pricelist_id(self):
        res = super(SaleOrder, self)._onchange_pricelist_id()
        self.incoterm = self.pricelist_id and self.pricelist_id.incoterm_id or False
        return res


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    cpo_line_no = fields.Char('CPO#')
    mpn = fields.Char('CMPN', help='Customer Manufacturer P/N')
    cpn = fields.Char('Customer P/N', help='Customer P/N')
    coo_id = fields.Many2one('res.country', 'COO')
    qty_remaining = fields.Float('Remaining Quantity', copy=False, compute='_compute_qty_remaining',  compute_sudo=True, store=True, digits='Product Unit of Measure', default=0.0)


    @api.depends('qty_delivered', 'product_uom_qty')
    def _compute_qty_remaining(self):
        for line in self:
            line.qty_remaining = line.product_uom_qty -  line.qty_delivered

    # def _get_display_price(self, product):
    #     prd_tmpl = product.product_tmpl_id.id
    #     pricelist_id = self.order_id.pricelist_id
    #
    #     cpn = self.cpn
    #     if cpn:
    #         rec = pricelist_id.price_line_moq_ids.filtered(lambda r: r.product_template_id.id == prd_tmpl and r.cpn == cpn)
    #     else:
    #         rec = pricelist_id.price_line_moq_ids.filtered(lambda r: r.product_template_id.id == prd_tmpl)
    #     rec = len(rec) > 0 and rec[0] or False
    #
    #     if rec:
    #         self.cpn = self.cpn or rec.cpn
    #         self.mpn = self.mpn or rec.cmpn or self.product_id.default_code
    #
    #         qty = self.product_uom_qty
    #         if qty >= rec.moq3 > 0:
    #             return rec.price3
    #         elif qty >= rec.moq2 > 0:
    #             return rec.price2
    #         elif qty >= rec.moq1:
    #             return rec.price1
    #         else:
    #             return 999
    #     return 999

    @api.onchange('cpn')
    def onchange_cpn(self):
        return self.product_id_change()

    def _get_display_price(self, product):

        qty = self.product_uom_qty
        prd_tmpl = product.product_tmpl_id.id
        pricelist_id = self.order_id.pricelist_id

        def filter_cpn(r):
            return r.product_tmpl_id.id == prd_tmpl and r.cpn == self.cpn and r.state == 'current'

        def filter_no_cpn(r):
            return r.product_tmpl_id.id == prd_tmpl and r.state == 'current'

        selected_filter = self.cpn and filter_cpn or filter_no_cpn
        pricelist_item_id = pricelist_id.item_ids.filtered(selected_filter)

        item_ids = pricelist_item_id.sorted(key='min_quantity', reverse=True)

        for item in item_ids:
            if qty >= item.min_quantity:
                self.cpn = item.cpn
                self.mpn = item.cmpn or self.product_id.default_code
                return item.fixed_price
        return 999

    def _prepare_invoice_line(self, **optional_values):
        vals = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
        description = vals.get('name', "")
        if self.cpn:
            description = f"Part Number: {self.cpn}\n" + description
        if self.mpn:
            description += f"\nMPN: {self.mpn}"
        if self.order_id.client_order_ref:
            description += f"\nCustomer PO#: {self.order_id.client_order_ref}"
        if self.cpo_line_no:
            description += f"\nPO Item: {self.cpo_line_no}"
        if self.coo_id:
            description += f"\nCountry of Origin: {self.coo_id.name}"
        vals.update({
            'name': description
            })
        return vals

    def _get_description_po_line(self, name):
        """Extended this method from ac_purchase_back2sale module
            to add purchase line description when it create from SO.
        """
        self.ensure_one()
        description = "Our Reference:"
        if self.cpn:
            description += '\n' + self.cpn
        if self.mpn:
            description += '\n' + self.mpn
        description += '\n' + self.name
        description += '\n\n' + 'Your Reference:'
        description = description + '\n' + name
        return description

    @api.model
    def _prepare_add_missing_fields(self, values):
        res = super(SaleOrderLine, self)._prepare_add_missing_fields(values)
        onchange_fields = ['cpn', 'mpn']
        if values.get('order_id') and values.get('product_id') and any(f not in values for f in onchange_fields):
            line = self.new(values)
            line.product_id_change()
            for field in onchange_fields:
                if field not in values:
                    res[field] = line._fields[field].convert_to_write(line[field], line)
        return res