# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.misc import clean_context
from odoo.exceptions import UserError, ValidationError

class StockMove(models.Model):
    _inherit = "stock.move"

    inter_procurement_id = fields.Many2one('stock.inter.procurement', 'Inter procurement')

class StockPicking(models.Model):
    _inherit = "stock.picking"

    inter_proc = fields.Char('Réapprovisionnement interne',compute='get_inter_id',search='search_inter_id')

    def search_inter_id(self, operator, value):
        procs = self.env['stock.inter.procurement'].sudo().search([('name', operator, value)], limit=None)
        moves = self.env['stock.move'].sudo().search([('inter_procurement_id', 'in', procs.ids)], limit=None)
        picks = moves.sudo().mapped('move_dest_ids').mapped('picking_id') | moves.sudo().mapped('move_orig_ids').mapped('picking_id') | moves.sudo().mapped('picking_id')
        return [('id', 'in', picks.sudo().ids)]

    def get_inter_id(self):
        for rec in self:
            inter_ids = rec.sudo().move_ids_without_package.mapped('inter_procurement_id') | rec.sudo().move_ids_without_package.mapped('move_dest_ids').mapped('inter_procurement_id') | \
                        rec.sudo().move_ids_without_package.mapped('move_orig_ids').mapped('inter_procurement_id')
            if not inter_ids:
                rec.inter_proc = ''
            else:
                if len(inter_ids) == 1:
                    rec.inter_proc = inter_ids.name
                else:
                    rec.inter_proc = '/'.join([inter.name for inter in inter_ids])

class StockRule(models.Model):
    _inherit = 'stock.rule'

    def _get_custom_move_fields(self):
        fields = super(StockRule, self)._get_custom_move_fields()
        fields += ['inter_procurement_id']
        return fields

class StockInterProcurement(models.Model):
    _name = 'stock.inter.procurement'

    name = fields.Char('Name', required=True, index=True, default=lambda self: _('New'),readonly=True,copy=False)
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
    date_planned = fields.Date('Date prévue',default=fields.Date.today(),required=True)

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
            'inter_procurement_id':line.inter_id.id,
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
