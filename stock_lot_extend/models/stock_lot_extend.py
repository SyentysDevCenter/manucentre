# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    tag_ids = fields.Many2many('product.tags', 'Etiquette')
    latest_price = fields.Float('Montant achat')
    suggested_price = fields.Float(u'Prix conseillé')
    categ_id = fields.Many2one('product.category', related='product_id.categ_id', store=True)