# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, timedelta, date

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
    
    picking_source_ids = fields.One2many('stock.picking', 'dispatch_id', string='Source Pickings')
    sale_dest_ids = fields.One2many('sale.order', 'dispatch_id', string='Associated Sale Orders')
    sales_count = fields.Float(compute='_compute_sales_count', string='Sale Orders', digits=0)
    
    company_id = fields.Many2one('res.company', string='Company', required=True)
    company_dest_ids = fields.Many2many('res.company', string='Destinations')
    
    line_ids = fields.One2many('stock.dispatch.line', 'dispatch_id', string='Lines')

    def _compute_sales_count(self):
        for dispatch in self:
            dispatch.sales_count = len(dispatch.sale_dest_ids.sudo().ids)
    
    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env.ref('dispatch.sequence_dispatch').next_by_id() or _('New')
        return super(StockDispatch, self).create(vals)

    def validate(self):
        for dispatch in self:
            orders = self.env['sale.order']
            lines_by_company = {}
            for line in dispatch.line_ids:
                partner = line.partner_id
                if not partner or line.qty_todo == 0:
                    continue
                category = line.category_id
                lines_by_company.setdefault(partner.id, {})
                lines_by_company[partner.id].setdefault(category.id, [])
                lines_by_company[partner.id][category.id].append([0, False, {
                    'product_id': line.product_id.id,
                    'product_uom_qty': line.qty_todo,
                    # Centrale sells products to the other companies with 3.2%
                    'price_unit': line.product_id.standard_price * 1.032
                }])
            _logger.warning(lines_by_company)
            for partner_id, lines_by_category in lines_by_company.items():
                for category_id, lines in lines_by_category.items():
                    order_id = self.env['sale.order'].create({
                        'partner_id': partner_id,
                        'order_line': lines,
                        'company_id': dispatch.company_id.id,
                        'dispatch_id': dispatch.id
                    })
                    orders |= order_id
            for order in orders:
                order.action_confirm()
            dispatch.state = 'done'

    def cancel(self):
        self.write({'state': 'cancel'})

    def action_view_sales(self):
        action_vals = {
            'name': _('Sale Orders'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', self.sale_dest_ids.ids)],
        }
        
        if len(self.sale_dest_ids) == 1:
            action_vals.update({'res_id': self.sale_dest_ids.id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals

    
class StockDispatchLine(models.Model):
    _name = 'stock.dispatch.line'
    _order = 'product_id'
    
    dispatch_id = fields.Many2one('stock.dispatch')
    company_id = fields.Many2one('res.company')
    partner_id = fields.Many2one(related='company_id.partner_id')
    category_id = fields.Many2one('product.category', compute='_compute_category_id')
    
    product_id = fields.Many2one('product.product', required=True, readonly=True)
    product_default_code = fields.Char(related='product_id.default_code', readonly=True)
    product_barcode = fields.Char(related='product_id.barcode', readonly=True)
    product_list_price = fields.Float(related='product_id.list_price', readonly=True)
    
    supplier_product_code = fields.Char('Supplier Code', compute='_compute_supplier')
    supplier_name = fields.Char('Supplier', compute='_compute_supplier')
    
    qty_todo = fields.Float('To Do')
    qty_available = fields.Float('Available', compute='_compute_qty_available')
    qty_dest_available = fields.Float('Dest. Available', compute='_compute_qty_dest_available')
    qty_dest_virtual_available = fields.Float('Dest. Forecast', compute='_compute_qty_dest_available')
    qty_dest_sold = fields.Float('Dest. Sold', compute='_compute_qty_dest_sold')
    
    warehouse_dest_id = fields.Many2one('stock.warehouse', string='Destination', readonly=True)
    
    @api.depends('product_id')
    def _compute_supplier(self):
        for line in self:
            if not line.product_id:
                line.update({
                    'supplier_product_code': False,
                    'supplier_name': False
                })
                continue
            product = line.product_id
            supplierinfo = self.env['product.supplierinfo'].search([
                ('product_tmpl_id', '=', product.product_tmpl_id.id),
                ('product_id', 'in', [False, product.id]),
                '|', ('date_end', '=', False),
                ('date_end', '>=', fields.Date.today())
            ], order='product_id', limit=1)
            if supplierinfo:
                line.update({
                    'supplier_product_code': supplierinfo.product_code,
                    'supplier_name': supplierinfo.name.name
                })
    
    @api.depends('product_id')
    def _compute_category_id(self):
        for line in self:
            if not line.product_id:
                line.category_id = False
                continue
            category = line.product_id.categ_id
            while category.parent_id and not category.dispatch_separation:
                category = category.parent_id
            line.category_id = category
    
    @api.depends('dispatch_id.company_id', 'product_id')
    def _compute_qty_available(self):
        for line in self:
            line.update({
                'qty_available': line.product_id.with_context(force_company=line.dispatch_id.company_id.id).sudo().qty_available
            })
    
    @api.depends('company_id', 'product_id')
    def _compute_qty_dest_available(self):
        for line in self:
            line.update({
                'qty_dest_available': line.product_id.with_context(force_company=line.company_id.id).sudo().qty_available,
                'qty_dest_virtual_available': line.product_id.with_context(force_company=line.company_id.id).sudo().virtual_available
            })
        
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
    