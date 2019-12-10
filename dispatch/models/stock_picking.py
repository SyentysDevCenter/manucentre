# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    source_dispatch_id = fields.Many2one('stock.dispatch', string='Dispatch', copy=False)
    dispatch_id = fields.Many2one('stock.dispatch', string='Dispatch', copy=False)
    type_code = fields.Selection('Type',related='picking_type_id.code')
    po_wh_id = fields.Many2one('stock.warehouse', string='PO WH', copy=False)
    so_done = fields.Boolean('SO crée')

    def action_create_so(self):
        orders = self.env['sale.order']
        partner_id = self.mapped('partner_id')
        if len(partner_id) > 1:
            raise UserError("Les transferts doivent appartenir au même partenaire!")
        all_dispatch = all([p.dispatch_id for p in self])
        if not all_dispatch:
            raise UserError("Les transferts doivent avoir une référence de dispatch!")
        lines_by_wh = {}
        for pick in self:
            route_id = False
            wh_id = self.env['stock.warehouse'].search([('company_id', '=', pick.company_id.id)], limit=1)
            if wh_id:
                route_id = wh_id.inter_route_id
            if not route_id:
                raise UserError(f"Aucune route de transfet inter-sociétés n'est définie pour l'entrepôt {wh_id.name}")
            if pick.so_done:
                raise UserError(f"Le transfert {pick.name} est déjà traité!")
            if not pick.po_wh_id:
                continue
            lines_by_wh.setdefault(pick.po_wh_id.id, [])
            for line in pick.move_ids_without_package:
                if line.quantity_done == 0:
                    continue
                lines_by_wh[pick.po_wh_id.id].append([0, False, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.quantity_done,
                    'route_id':route_id.id,
                }])
        for wh_id, lines in lines_by_wh.items():
            po_picking_type_id = False
            picking_type_id = self.env['stock.picking.type'].search([
                ('code', '=', 'incoming'), ('warehouse_id', '=', wh_id)
            ], limit=1)
            if picking_type_id:
                po_picking_type_id = picking_type_id.id
            order_id = self.env['sale.order'].create({
                'partner_id': partner_id.id,
                'order_line': lines,
                'company_id': pick.company_id.id,
                'po_picking_type_id': po_picking_type_id,
                'origin': f'{pick.name}:{pick.dispatch_id.name}'
            })
            orders |= order_id
        self.so_done = True
        orders.action_confirm()