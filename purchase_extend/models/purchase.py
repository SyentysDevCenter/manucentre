# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    ref_variante = fields.Char(related='product_id.ref_variante', string='Réference variante', store=True)
