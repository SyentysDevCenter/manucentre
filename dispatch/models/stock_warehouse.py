# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    supplier_location_id = fields.Many2one('stock.location', string='Emplecement Fournisseur')
