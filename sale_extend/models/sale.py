# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    margin_percent = fields.Float(string='Marge(%)',related='product_id.margin_percent')
    sale_purchase_price = fields.Float(string="Prix d'achat",related='product_id.purchase_price')
    sales_margin_percent = fields.Float(string='Marge commerciale(%)',related='product_id.sales_margin_percent')