# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrderCreate(models.TransientModel):
    _name='purchase.order.create'
    _description = 'Wizard to create Purchase Order'


    @api.model
    def default_get(self, fields):
        rec = super(PurchaseOrderCreate, self).default_get(fields)
        product_ids = []
        for product in self.env.context.get('active_ids'):
             product_id= self.env['purchase.order.line.create'].create({'product_id':product,
                                })
             product_ids.append(product_id.id)
        rec['product_ids'] = product_ids
        warehouse = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)])
        rec['warehouse_id'] = warehouse and warehouse[0].id
        return rec



    partner_id = fields.Many2one("res.partner", required=True)
    product_ids = fields.One2many("purchase.order.line.create", 'rec_id')
    warehouse_id = fields.Many2one('stock.warehouse')


    def _prepare_purchase_order(self):
        self.ensure_one()
        picking_type = self.env['purchase.order']._get_picking_type(self.env.context.get('company_id') or self.env.company.id)

        return {
            'partner_id': self.partner_id.id,
            'company_id': self.env.user.company_id.id,
            'currency_id': self.env.user.company_id.currency_id.id,
            'picking_type_id': picking_type and picking_type.id,

        }

    def _prepare_line_group(self, product):
        return [{
            'product_id': product.product_id.id,
            'name':  product.product_id.name,
            'product_qty' : product.qty,
            'product_uom' : product.product_id.uom_po_id.id,
            'price_unit' : 0,
            'date_planned' : fields.Date.context_today(self),
            'taxes_id' : [(6, 0,product.product_id.supplier_taxes_id.mapped('id'))],
        } ]

    def validate(self):
        self.ensure_one()
        lines = []
        for product in self.product_ids:
            lines.extend(self._prepare_line_group(product))
        vals = self._prepare_purchase_order()
        # vals['order_line'] = lines
        purchase_id = self.env['purchase.order'].create(vals)
        for line in lines:
            line['order_id'] = purchase_id.id
            l =  self.env['purchase.order.line'].create(line)
            l.onchange_product_id()

        action_vals = {
            'name': ('Purchase Order'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'purchase.order',
            'domain': [('id ', 'in', purchase_id.ids)],
        }

        if len(purchase_id) == 1:
            action_vals.update({'res_id': purchase_id.id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals


class PurchaseOrderLineCreate(models.TransientModel):
    _name = 'purchase.order.line.create'

    product_id = fields.Many2one('product.product')
    name = fields.Text(required=True)
    qty = fields.Float('Quantité', default='1')
    rec_id = fields.Many2one('purchase.order.create')
    product_uom = fields.Many2one('uom.uom')
    price_unit = fields.Float('Cost', digits='Product Price', required=True)
    taxes_id = fields.Many2many('account.tax')
    price_subtotal = fields.Float('Total', digits='Product Price', required=True)







