# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    margin_percent = fields.Float(string='Marge(%)',compute='get_margin',store=True)
    sale_purchase_price = fields.Float(string="Prix d'achat",related='product_id.purchase_price')
    sales_margin_percent = fields.Float(string='Marge commerciale(%)',compute='get_margin',store=True)
    ref_variante = fields.Char(string='Réference fournisseur',related='product_id.ref_variante')
    purchase_price = fields.Float(readonly=True)

    @api.depends('product_id','price_unit')
    def get_margin(self):
        for rec in self:
            purchase_tax = sum([tax.amount for tax in rec.product_id.product_tmpl_id.supplier_taxes_id]) / 100
            rec.margin_percent = (rec.price_unit - rec.product_id.standard_price * (1 + purchase_tax)) / (rec.price_unit or 1.0) * 100
            rec.sales_margin_percent = (rec.price_unit - rec.sale_purchase_price * (1 + purchase_tax)) / (rec.price_unit or 1.0) * 100

    def _compute_tax_id(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id or line.order_id.partner_id.property_account_position_id
            # If company_id is set, always filter taxes by the company
            taxes = line.product_id.taxes_id.filtered(lambda r: not line.order_id.company_id or r.company_id == line.order_id.company_id)
            line.tax_id = fpos.map_tax(taxes, line.product_id, line.order_id.partner_shipping_id) if fpos else taxes
