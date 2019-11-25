# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class StockOrder(models.Model):
    _inherit = 'sale.order'

    po_picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        domain="[('code', '=', 'incoming'), ('company_id', '=', company_id)]")

    def _prepare_purchase_order_data(self, company, company_partner):
        print("*"*50)
        print("_prepare_purchase_order_data")
        print("*"*50)
        res = super(StockOrder, self)._prepare_purchase_order_data(company, company_partner)
        if self.po_picking_type_id:
            res['picking_type_id'] = self.po_picking_type_id.id
        return res