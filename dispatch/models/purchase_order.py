# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    dispatch_id = fields.Many2one(related='auto_sale_order_id.dispatch_id', readonly=True, copy=False)
