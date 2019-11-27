# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.misc import clean_context
from odoo.exceptions import UserError, ValidationError

class StockInterProcurement(models.Model):
    _name = 'stock.inter.procurement'

    name = fields.Char('Name', required=True, index=True, default=lambda self: _('New'),readonly=True)
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('done', 'Done')
    ], default='draft')
    date = fields.Date("Date", required=True, default=fields.Date.today())
    warehouse_id = fields.Many2one('stock.warehouse', string="Entrepôt", required=True)
    route_id = fields.Many2one('stock.location.route', string='Route logistique')
    line_ids = fields.One2many('stock.inter.line', 'inter_id', string='Lines')
    date_planned = fields.Date('Date prévue')

    def unlink(self):
        if 'done' in self.mapped('state'):
            raise UserError(_("Le document ne peut pas être supprimer dans cet état!"))
        return super(StockInterProcurement, self).unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env.ref('inter_procurement.sequence_inter_procurement').next_by_id() or _('New')
        return super(StockInterProcurement, self).create(vals)

    def _prepare_run_values(self,line):
        replenishment = self.env['procurement.group'].create({
            'partner_id': line.product_id.with_context(
                force_company=line.inter_id.company_id.id).responsible_id.partner_id.id,
        })

        values = {
            'warehouse_id': line.inter_id.warehouse_id,
            'route_ids': line.inter_id.route_id,
            'date_planned': line.inter_id.date_planned,
            'group_id': replenishment,
        }
        return values

    def validate(self):
        for rec in self:
            for line in rec.line_ids:
                try:
                    self.env['procurement.group'].with_context(clean_context(self.env.context)).run([
                        self.env['procurement.group'].Procurement(
                            line.product_id,
                            line.quantity,
                            line.product_id.uom_id,
                            rec.warehouse_id.lot_stock_id,  # Location
                            _("Manual Replenishment"),  # Name
                            _("Manual Replenishment"),  # Origin
                            rec.company_id,
                            self._prepare_run_values(line)  # Values
                        )
                    ])
                except UserError as error:
                    raise UserError(error)
            rec.state = 'done'


    def cancel(self):
        self.write({'state': 'cancel'})

class StockDispatchLine(models.Model):
    _name = 'stock.inter.line'

    inter_id = fields.Many2one('stock.inter.procurement')
    product_id = fields.Many2one('product.product',required=True)
    quantity = fields.Float('Quantité')
