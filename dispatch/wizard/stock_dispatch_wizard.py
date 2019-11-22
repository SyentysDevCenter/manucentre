# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

import logging

_logger = logging.getLogger(__name__)


class StockDispatchWizard(models.TransientModel):
    _name = 'stock.dispatch.wizard'
    _description = 'Wizard to create dispatch'
    
    def _domain_default_destination(self):
        return []
    
    @api.model
    def _get_default_destination(self):        
        domain = self._domain_default_destination()
        return self.env['res.company'].search(domain)
    
    def _get_default_company(self):
        return self.env.user.company_id
    
    @api.model
    def _get_default_origin(self):
        pickings = self.env['stock.picking'].browse(self._context.get('active_ids'))
        if pickings:
            return ', '.join(pickings.mapped('name'))
        return False
    
    @api.model
    def _get_default_source(self):
        return self.env['stock.picking'].browse(self._context.get('active_ids'))
    
    company_id = fields.Many2one("res.company", default=_get_default_company)
    company_dest_ids = fields.Many2many('res.company', string='Destinations', default=_get_default_destination)
    picking_source_ids = fields.Many2many('stock.picking', string='Source Pickings', default=_get_default_source)
    origin = fields.Char("Origin/Object", required=True, default=_get_default_origin)

    def _prepare_dispatch(self):
        self.ensure_one()
        return {
            'origin': self.origin,
            'company_id': self.company_id.id,
            'company_dest_ids': [(6, False, self.company_dest_ids.ids)],
        }

    def _prepare_line_group(self, product):
        return [(0, False, {
            'product_id': product,
            'warehouse_dest_id': company.sudo().warehouse_id.id,
            'company_id': company.id,
        }) for company in self.company_dest_ids]

    def validate(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        
        product_ids = []
        if active_model == 'stock.picking':
            for picking in self.env['stock.picking'].browse(active_ids):
                if picking.move_lines:
                    product_ids.extend(picking.move_lines.mapped('product_id.id'))
                if hasattr(picking, 'pack_operation_ids') and picking.pack_operation_ids:
                    product_ids.extend(picking.pack_operation_ids.mapped('product_id.id'))
            
        lines = []
        for product in list(set(product_ids)):
            lines.extend(self._prepare_line_group(product))
        vals = self._prepare_dispatch()
        vals['line_ids'] = lines
        dispatch_id = self.env['stock.dispatch'].create(vals)
        self.picking_source_ids.write({
            'dispatch_id': dispatch_id.id
        })
        
        action_vals = {
            'name': _('Dispatch'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'stock.dispatch',
            'domain': [('id', 'in', dispatch_id.ids)],
        }
        
        if len(dispatch_id) == 1:
            action_vals.update({'res_id': dispatch_id.id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        
        return action_vals
        