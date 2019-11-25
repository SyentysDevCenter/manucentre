# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    source_dispatch_id = fields.Many2one('stock.dispatch', string='Dispatch', copy=False)
    dispatch_id = fields.Many2one('stock.dispatch', string='Dispatch', copy=False)
    type_code = fields.Selection('Type',related='picking_type_id.code')

    def action_create_so(self):
        partner_id = self.mapped('partner_id')
        if len(partner_id) > 1:
            raise UserError("Les transferts doivent appartenir au même partenaire!")
        for pick in self:
            lines_by_company = []
            for line in pick.move_ids_without_package:
                partner = partner_id
                if not partner or line.quantity_done == 0:
                    continue
                lines_by_company.append([0, False, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity_done
                }])
        order_id = self.env['sale.order'].create({
            'partner_id': partner_id.id,
            'order_line': lines_by_company,
            'company_id': pick.company_id.id,
        })
        order_id.action_confirm()