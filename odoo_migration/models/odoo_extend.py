from odoo import api, fields, models


class Product(models.Model):
    _inherit = 'product.product'

    old_id = fields.Integer(string='Old id', readonly=True)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    old_id = fields.Integer(string='Old id', readonly=True)

class ProductCateg(models.Model):
    _inherit = 'product.category'

    old_id = fields.Integer(string='Old id', readonly=True)


class ResPartner(models.Model):
    _inherit = 'res.partner'

    old_id = fields.Integer(string='Old id', readonly=True)


class StockProductLot(models.Model):
    _inherit = 'stock.production.lot'

    old_id = fields.Integer(string='Old id', readonly=True)
