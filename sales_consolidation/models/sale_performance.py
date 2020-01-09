# -*- coding: utf-8 -*-

from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import fields, models,api, tools


class SalePerformance(models.Model):
    _name = "sale.performance"
    _description = "CA commercial"

    date = fields.Date('Date')
    name = fields.Char('Reference')
    product_id = fields.Many2one("product.product",string='Article')
    quantity = fields.Float("Quantité")
    cost = fields.Float(string='Coût',related='product_id.standard_price',store=True,groups='product_extend.group_show_product_cost')
    margin = fields.Float(string='Marge', related='product_id.margin',store=True,groups='product_extend.group_show_product_cost')
    margin_percent = fields.Float(string='Marge(%)',group_operator="avg",related='product_id.margin_percent',store=True,groups='product_extend.group_show_product_cost')
    purchase_price = fields.Float("Prix d'achat",related='product_id.purchase_price',store=True)
    sales_margin = fields.Float(string='Marge commerciale',related='product_id.sales_margin',store=True)
    sales_margin_percent = fields.Float(string='Marge commerciale(%)',group_operator="avg",related='product_id.sales_margin_percent',store=True)
    type = fields.Selection([('pos', 'POS'),('sale', 'Vente')], string="Type")
    price_unit = fields.Float('Prix unitaire')
    price = fields.Float('Prix')
    categ_id = fields.Many2one('product.category',string='Catégorie',related='product_id.product_tmpl_id.categ_id',store=True)
    company_id = fields.Many2one('res.company',string='Société')
    user_id = fields.Many2one('res.users',string='Vendeur')
    warehouse_id = fields.Many2one('stock.warehouse',string='Entrepôt')

    @api.model
    def action_get_turn_over(self):
        sale_perf_obj = self.env['sale.performance']
        sale_obj = self.env['sale.order']
        pos_obj = self.env['pos.order']
        action = self.env.ref('sales_consolidation.sale_performance_action').read()[0]
        sale_perf_obj.sudo().search([]).unlink()
        sale_ids = sale_obj.sudo().search([])
        pos_ids = pos_obj.sudo().search([])
        for sale in sale_ids:
            for line in sale.order_line:
                sale_perf_obj.sudo().create(
                    {
                        'date': sale.date_order,
                        'type': 'sale',
                        'name': sale.name,
                        'product_id': line.product_id.id,
                        'quantity': line.product_uom_qty,
                        'price_unit': line.price_unit,
                        'price': line.product_uom_qty*line.price_unit,
                        'company_id': sale.company_id.id,
                        'user_id': sale.user_id.id,
                        'warehouse_id': sale.warehouse_id.id,
                    }
                )
        for pos in pos_ids:
            for line in pos.lines:
                sale_perf_obj.sudo().create(
                    {
                        'date': pos.date_order,
                        'type': 'pos',
                        'name': pos.name,
                        'product_id': line.product_id.id,
                        'quantity': line.qty,
                        'price_unit': line.price_unit,
                        'price': line.price_unit*line.qty,
                        'company_id': pos.company_id.id,
                        'user_id': pos.user_id.id,
                        'warehouse_id': pos.picking_id.picking_type_id.warehouse_id.id,
                    }
                )
        return action