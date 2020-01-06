# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class StockDispatch(models.Model):
    """Dispatch creates sale orders from an incoming picking."""
    _name = 'stock.dispatch'

    name = fields.Char('Name', required=True, index=True, default=lambda self: _('New'))

    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('done', 'Done')
    ], default='draft')

    origin = fields.Char('Origin')
    date = fields.Date("Date", required=True, default=fields.Date.today())

    picking_source_ids = fields.One2many('stock.picking', 'source_dispatch_id', string='Source Pickings')

    picking_ids = fields.One2many('stock.picking', 'dispatch_id', string='Pickings')

    company_id = fields.Many2one('res.company', string='Company', required=True)
    wh_ids = fields.Many2many('stock.warehouse', string='Destinations')
    wh_id = fields.Many2one('stock.warehouse', string='Source')

    line_ids = fields.One2many('stock.dispatch.line', 'dispatch_id', string='Lines')

    picking_count = fields.Integer(string='# Pickings', compute="get_picking_count")

    def unlink(self):
        if 'done' in self.mapped('state'):
            raise UserError(_("Le dispatch ne peut pas être supprimer dans cet état!"))
        return super(StockDispatch, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env.ref('dispatch.sequence_dispatch').next_by_id() or _('New')
        return super(StockDispatch, self).create(vals)

    def validate(self):
        for dispatch in self:
            pickings = self.env['stock.picking']
            lines_by_company = {}
            transit_loc = self.env['stock.location'].search(
                [('company_id', '=', dispatch.company_id.id), ('usage', '=', 'transit')], limit=1)
            if not transit_loc:
                raise UserError(
                    _(f"Aucun emplacement de transit n'est défini pour la société {dispatch.company_id.name}!"))
            for line in dispatch.line_ids:
                wh_id = line.wh_id
                if not wh_id or line.qty_todo == 0:
                    continue
                lines_by_company.setdefault(wh_id.id, [])
                if not line.product_id.tracking == 'serial':
                    lines_by_company[wh_id.id].append([0, False, {
                        'name': line.product_id.name,
                        'product_uom': line.product_id.uom_id.id,
                        'product_id': line.product_id.id,
                        'quantity_done': line.qty_todo,
                        'location_id': dispatch.wh_id.lot_stock_id.id,
                        'location_dest_id': transit_loc.id,
                    }])
                else:
                    for num in range(int(line.qty_todo)):
                        lines_by_company[wh_id.id].append([0, False, {
                            'name': line.product_id.name,
                            'product_uom': line.product_id.uom_id.id,
                            'product_id': line.product_id.id,
                            'quantity_done': 1,
                            'location_id': dispatch.wh_id.lot_stock_id.id,
                            'location_dest_id': transit_loc.id,
                        }])
            for wh_id, lines in lines_by_company.items():
                wh_id = self.env['stock.warehouse'].browse(wh_id)
                pick_id = self.env['stock.picking'].create({
                    'partner_id': wh_id.company_id.partner_id.id,
                    'picking_type_id': dispatch.wh_id.int_type_id.id,
                    'location_id': dispatch.wh_id.lot_stock_id.id,
                    'location_dest_id': transit_loc.id,
                    'move_ids_without_package': lines,
                    'company_id': dispatch.company_id.id,
                    'dispatch_id': dispatch.id,
                    'po_wh_id': wh_id.id,
                    'origin': dispatch.name,
                })
                pickings |= pick_id
            dispatch.state = 'done'

    def cancel(self):
        self.write({'state': 'cancel'})

    def get_picking_count(self):
        for rec in self:
            rec.picking_count = len(rec.picking_ids)

    def action_view_picking(self):
        action_vals = {
            'name': _('Pickings'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'stock.picking',
            'domain': [('id', 'in', self.picking_ids.ids)],
        }

        if len(self.picking_ids) == 1:
            action_vals.update({'res_id': self.picking_ids.id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals


class StockDispatchLine(models.Model):
    _name = 'stock.dispatch.line'
    _order = 'product_id'

    dispatch_id = fields.Many2one('stock.dispatch')
    wh_id = fields.Many2one('stock.warehouse', readonly=True, string="Entrepôt")
    company_id = fields.Many2one('res.company', related='wh_id.company_id')
    partner_id = fields.Many2one(related='company_id.partner_id', string='Société (Dest)')
    product_id = fields.Many2one('product.product', required=True, readonly=True, string='Article')
    product_default_code = fields.Char(related='product_id.default_code', readonly=True, string='Code')
    product_barcode = fields.Char(related='product_id.barcode', readonly=True, string='Code à barres')
    product_list_price = fields.Float(related='product_id.list_price', readonly=True, string="Prix de vente")

    supplier_product_code = fields.Char('Code fournisseur', compute='_compute_supplier')
    supplier_name = fields.Char('Fournisseur', compute='_compute_supplier')

    qty_todo = fields.Float('A faire')
    qty_available = fields.Float('Disponible', compute='_compute_qty_available')
    qty_dest_available = fields.Float('Disponible (Dest)', compute='_compute_qty_dest_available')
    qty_dest_virtual_available = fields.Float('Prévue (Dest)', compute='_compute_qty_dest_available')
    qty_dest_sold = fields.Float('Vendue (Dest)', compute='_compute_qty_dest_sold')

    @api.depends('product_id')
    def _compute_supplier(self):
        for line in self:
            product = line.product_id
            supplierinfo = self.env['product.supplierinfo'].search([
                ('product_tmpl_id', '=', product.product_tmpl_id.id),
                ('product_id', 'in', [False, product.id]),
                '|', ('date_end', '=', False),
                ('date_end', '>=', fields.Date.today())
            ], order='product_id', limit=1)
            if supplierinfo:
                line.supplier_product_code = supplierinfo.product_code,
                line.supplier_name = supplierinfo.name.name

    @api.depends('dispatch_id.company_id', 'product_id')
    def _compute_qty_available(self):
        for line in self:
            line.qty_available = line.product_id.with_context(
                force_company=line.dispatch_id.company_id.id).sudo().qty_available

    @api.depends('company_id', 'product_id')
    def _compute_qty_dest_available(self):
        for line in self:
            line.qty_dest_available = line.product_id.with_context(
                force_company=line.company_id.id).sudo().qty_available
            line.qty_dest_virtual_available = line.product_id.with_context(
                force_company=line.company_id.id).sudo().virtual_available

    @api.depends('company_id', 'product_id')
    def _compute_qty_dest_sold(self):
        for line in self:
            order_line_ids = self.env['sale.order.line'].sudo().search([
                ('product_id', '=', line.product_id.id),
                ('company_id', '=', line.company_id.id),
                ('order_id.state', 'in', ['sale', 'done']),
                ('order_id.date_order', '<=', fields.Date.to_string(date.today())),
                ('order_id.date_order', '>=', fields.Date.to_string(date.today() - timedelta(days=365)))
            ])
            line.qty_dest_sold = sum(order_line_ids.mapped('product_uom_qty'))
