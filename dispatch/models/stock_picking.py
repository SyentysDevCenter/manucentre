# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    dispatch_id = fields.Many2one('stock.dispatch', string='Dispatch', copy=False)
