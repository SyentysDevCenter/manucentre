# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProductTemplate(models.Model):
    _name = 'product.stock.tag'

    name = fields.Char('Stock')
    color = fields.Integer(string='Color Index')


class ProductProduct(models.Model):
    _inherit = 'product.product'

    stock_tags = fields.Many2many('product.stock.tag', string="Stock par société",compute="_get_stock_tags")

    def _get_stock_tags(self):
        for rec in self:
            tags = self.env['product.stock.tag']
            whs = self.sudo().env['stock.warehouse'].search([])
            color = 1
            for wh in whs:
                stock = self.sudo().env['stock.quant']._get_available_quantity(rec, wh.lot_stock_id)
                tags |= self.env['product.stock.tag'].create(
                    {'name':f"{wh.name}:{stock}",'color':color}
                )
                color += 1
            rec.stock_tags = tags


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    stock_tags = fields.Many2many('product.stock.tag', string="Stock par société",compute="_get_stock_tags")


    def _get_stock_tags(self):
        for rec in self:
            tags = self.env['product.stock.tag']
            whs = self.sudo().env['stock.warehouse'].search([])
            color = 1
            for wh in whs:
                stock = 0
                for p in rec.product_variant_ids:
                    stock += self.sudo().env['stock.quant']._get_available_quantity(p, wh.lot_stock_id)
                tags |= self.env['product.stock.tag'].create(
                    {'name':f"{wh.name}:{stock}",'color':color}
                )
                color += 1
            rec.stock_tags = tags