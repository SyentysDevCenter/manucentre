# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.osv import expression


class ProductProduct(models.Model):
    _inherit = 'product.product'

    margin = fields.Float(string='Marge',compute="_get_margin")
    margin_percent = fields.Float(string='Marge(%)', compute="_get_margin")
    purchase_price = fields.Float("Prix d'achat")
    sales_margin = fields.Float(string='Marge commerciale', compute="_get_margin")
    sales_margin_percent = fields.Float(string='Marge commerciale(%)', compute="_get_margin")
    product_tags_ids = fields.Many2many('product.tags', string="Tags")
    product_brand_id = fields.Many2one('product.brand', string="Marque", related='product_tmpl_id.product_brand_id')

    ref_variante = fields.Char(string='Réference variante', compute="_get_ref", store=True)

    @api.depends('variant_seller_ids', 'variant_seller_ids.product_code')
    def _get_ref(self):
        for rec in self:
            if rec.variant_seller_ids:
                sellers = rec.variant_seller_ids.filtered(lambda r:r.product_code)
                if sellers:
                    rec.ref_variante = sellers[0].product_code

    # @api.model
    # def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
    #
    #     domain = expression.OR(
    #             [args or [], [('ref_variante','ilike', name)]])
    #     print('domaaaaaaaaaaaaaaaa', domain)
    #     return super(ProductProduct, self.sudo())._name_search(name=name, args=domain, operator=operator, limit=limit,
    #                                                           name_get_uid=name_get_uid)


    # @api.model
    # def name_search(self, name='', args=None, operator='ilike', limit=100):
    #     # res = super(ProductProduct, self).name_search(name='', args=None, operator='ilike', limit=100)
    #
    #     args = args or []
    #     domain = []
    #
    #
    #     domain = [('ref_variante', operator, name)]
    #     domain =  expression.OR([domain, args])
    #     return super(ProductProduct, self).name_search(name=name, args=domain, operator=operator, limit=limit)




    def _get_margin(self):
        for rec in self:
            purchase_tax = sum([tax.amount for tax in rec.product_tmpl_id.supplier_taxes_id])/100
            rec.margin = rec.lst_price - rec.standard_price
            rec.margin_percent = (rec.lst_price - rec.standard_price*(1+purchase_tax))/(rec.lst_price or 1.0)*100
            rec.sales_margin = rec.lst_price - rec.purchase_price
            rec.sales_margin_percent = (rec.lst_price - rec.purchase_price*(1+purchase_tax))/(rec.lst_price or 1.0)*100