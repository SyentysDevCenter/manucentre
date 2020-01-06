# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = "Marque d'article"

    name = fields.Char(required=True)

