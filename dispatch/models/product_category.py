# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ProductCategory(models.Model):
    _inherit = 'product.category'

    dispatch_separation = fields.Boolean('Separate on dispatch')
