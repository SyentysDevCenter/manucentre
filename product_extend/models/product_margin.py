# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    margin = fields.Float(string='Marge',compute="_get_margin")
    margin_percent = fields.Float(string='Marge(%)', compute="_get_margin")

    def _get_margin(self):
        for rec in self:
            rec.margin = rec.lst_price - rec.standard_price
            rec.margin_percent = (rec.margin / (rec.standard_price or 1.0))*100