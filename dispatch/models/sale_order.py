# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    dispatch_id = fields.Many2one('stock.dispatch', string='Dispatch', copy=False)
