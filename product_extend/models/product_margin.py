# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    margin = fields.Float(string='Marge',compute="_get_margin")
    margin_percent = fields.Float(string='Marge(%)', compute="_get_margin")
    purchase_price = fields.Float("Prix d'achat")
    sales_margin = fields.Float(string='Marge commerciale', compute="_get_margin")
    sales_margin_percent = fields.Float(string='Marge commerciale(%)', compute="_get_margin")

    def _get_margin(self):
        for rec in self:
            purchase_tax = sum([tax.amount for tax in rec.product_tmpl_id.supplier_taxes_id])/100
            rec.margin = rec.lst_price - rec.standard_price
            rec.margin_percent = (rec.lst_price - rec.standard_price*(1+purchase_tax))/(rec.lst_price or 1.0)*100
            rec.sales_margin = rec.lst_price - rec.purchase_price
            rec.sales_margin_percent = (rec.lst_price - rec.purchase_price*(1+purchase_tax))/(rec.lst_price or 1.0)*100