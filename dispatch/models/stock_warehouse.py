# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    inter_route_id = fields.Many2one('stock.location.route', string='Route livraison inter-sociétés')
