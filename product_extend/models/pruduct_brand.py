from odoo import api, fields, models


class ProductBrand(models.Model):
    _name = 'product.brand'
    _description = "Marque d'article"

    name = fields.Char(required=True)


class ProductTags(models.Model):
     _name = 'product.tags'
     _parent_name = "parent_id"
     _parent_store = True
     _description = 'Product tags'

     name = fields.Char(required=True)
     active = fields.Boolean(help='The active field allows you to hide the tag without removing it.', default=True)
     parent_id = fields.Many2one(string='Parent', comodel_name='product.tags', index=True,  ondelete='cascade')
     parent_path = fields.Char(index=True)
     display_name = fields.Char('Full Name', compute='_compute_display_name')

     child_ids = fields.One2many(string='Child Tags', comodel_name='product.tags', inverse_name='parent_id')


     @api.depends('name', 'parent_id.name')
     def _compute_display_name(self):
         """ Return the tags' display name, including their direct parent. """
         for rec in self:
             if rec.parent_id:
                 rec.display_name = rec.parent_id.display_name + ' / ' + rec.name
             else:
                 rec.display_name = rec.name

     @api.model
     def name_search(self, name, args=None, operator='ilike', limit=100):
         args = args or []
         if name:
             # Be sure name_search is symetric to name_get
             name = name.split(' / ')[-1]
             args = [('name', operator, name)] + args
         tags = self.search(args, limit=limit)
         return tags.name_get()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    product_brand_id = fields.Many2one('product.brand', string="Marque")


class ProductProduct(models.Model):
    _inherit = 'product.product'

    product_tags_ids = fields.Many2many('product.tags', string="Tags")