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
    product_tags_ids = fields.Many2many('product.tags', 'product_product_tags_rel', 'product_id', 'tag_id',
                                        string="Tags")
    product_brand_id = fields.Many2one('product.brand', string="Marque", related='product_tmpl_id.product_brand_id')

    ref_variante = fields.Char(string='Réference fournisseur', compute="_get_ref", store=True)

    @api.depends('variant_seller_ids', 'variant_seller_ids.product_code')
    def _get_ref(self):
        for rec in self:
            if rec.variant_seller_ids:
                sellers = rec.variant_seller_ids.filtered(lambda r:r.product_code).sorted(key=lambda r: str(r.create_date), reverse=True)
                if sellers:
                    s_price = sellers[0]
                    for s in sellers:
                        if s.product_id == rec:
                            s_price = s
                            break
                    for s in sellers:
                        if s.create_date:
                            s_price = s
                            break
                    rec.ref_variante = s_price.product_code


    def _get_margin(self):
        for rec in self:
            purchase_tax = sum([tax.amount for tax in rec.product_tmpl_id.supplier_taxes_id])/100
            rec.margin = rec.lst_price - rec.standard_price
            rec.margin_percent = (rec.lst_price - rec.standard_price*(1+purchase_tax))/(rec.lst_price or 1.0)*100
            rec.sales_margin = rec.lst_price - rec.purchase_price
            rec.sales_margin_percent = (rec.lst_price - rec.purchase_price*(1+purchase_tax))/(rec.lst_price or 1.0)*100