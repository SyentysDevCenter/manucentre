from odoo import api, fields, models


class ProductBrand(models.Model):

    _name = 'product.brand'

    name = fields.Char(required=True)


class ProductTags(models.Model):
     _name = 'product.tags'

     name = fields.Char(required=True)

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_brand_id = fields.Many2one('product.brand', string="Marque")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_tags_ids = fields.Many2many('product.tags', string="Tags")