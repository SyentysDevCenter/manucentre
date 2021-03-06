# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

import logging

_logger = logging.getLogger(__name__)


class ProductDispatchWizard(models.TransientModel):
    _name = 'product.dispatch.wizard'
    _description = 'Wizard to create dispatch'
    
    def _domain_default_destination(self):
        return [('company_id', '!=', self.env.user.company_id.id)]
    
    @api.model
    def _get_default_destination(self):        
        domain = self._domain_default_destination()
        return self.env['stock.warehouse'].search(domain)
    
    def _get_default_company(self):
        return self.env.user.company_id
    
    @api.model
    def _get_default_origin(self):
        products = self.env['product.product'].browse(self._context.get('active_ids'))
        # source_dispatch_id = products.mapped('source_dispatch_id')
        # if source_dispatch_id:
        #     raise UserError("Certain transferts sont déjà distribués!")
        if products:
            return ', '.join(products.mapped('name'))
        return False
    
    @api.model
    def _get_default_source(self):
        return self.env['product.product'].browse(self._context.get('active_ids'))
    
    company_id = fields.Many2one("res.company", default=_get_default_company)
    wh_id = fields.Many2one('stock.warehouse',string='Source',required=True)
    wh_ids = fields.Many2many('stock.warehouse', string='Destinations', default=_get_default_destination, domain="[('company_id', '!=', company_id)]")
    product_source_ids = fields.Many2many('product.product', string='Source Products', default=_get_default_source)
    origin = fields.Char("Origin/Object", required=True, default=_get_default_origin)

    def _prepare_dispatch(self):
        self.ensure_one()
        return {
            'origin': self.origin,
            'company_id': self.company_id.id,
            'wh_id':self.wh_id.id,
            'wh_ids': [(6, False, self.wh_ids.ids)],
        }

    def _prepare_line_group(self, product):
        return [(0, False, {
            'product_id': product,
            'wh_id': wh_id.id,
            'company_id': wh_id.company_id.id,
        }) for wh_id in self.sudo().wh_ids]

    def validate(self):
        self.ensure_one()
        active_ids = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        
        product_ids = []
        if active_model == 'product.product':
            for product in self.env['product.product'].browse(active_ids):
                product_ids.extend(product.seller_ids.mapped('product_id.id'))

        lines = []
        for product in list(set(product_ids)):
            lines.extend(self._prepare_line_group(product))
        vals = self._prepare_dispatch()
        vals['line_ids'] = lines
        dispatch_id = self.env['stock.dispatch'].create(vals)
        # self.product_source_ids.write({
        #     # 'source_dispatch_id': dispatch_id.id
        # })
        
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