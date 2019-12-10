# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

JOURNAL_TYPE_MAP = {
                    ('outgoing', 'customer'): ['sale'],
                    ('incoming', 'supplier'): ['purchase'],
                    }

class StockInvoiceOnshipping(models.TransientModel):
    _name = "stock.invoice.onshipping"
    _description = "Stock Invoice Onshipping"

    #Default Journal
    @api.model
    def _get_journal(self):
        company_id = False
        allowed_company_ids= self.env.context.get('allowed_company_ids',False)
        if allowed_company_ids:
            company_id = allowed_company_ids[0]
        journal_obj = self.env['account.journal']
        res_ids = self.env.context.get('active_ids')
        pick_obj = self.env['stock.picking']
        pickings = pick_obj.browse(res_ids)
        picking_type_id = pickings.mapped('picking_type_id')
        if picking_type_id.mapped('code')[0] == 'incoming':
            journals = journal_obj.search([('type', '=', 'purchase'),('company_id','=',company_id)])
        elif picking_type_id.mapped('code')[0] == 'outgoing':
            journals = journal_obj.search([('type', '=', 'sale'),('company_id','=',company_id)])
        else:
            raise UserError("Seules les livraisons / réceptions peuvent être facturés!")
        return journals and journals[0] or False

    @api.model
    def _journal_domain(self):
        company_id = False
        allowed_company_ids = self.env.context.get('allowed_company_ids', False)
        if allowed_company_ids:
            company_id = allowed_company_ids[0]
        res_ids = self.env.context.get('active_ids')
        pick_obj = self.env['stock.picking']
        pickings = pick_obj.browse(res_ids)
        picking_type_id = pickings.mapped('picking_type_id')
        domain = []
        if picking_type_id.mapped('code'):
            if picking_type_id.mapped('code')[0] == 'incoming':
                domain = [('type', '=', 'purchase'),('company_id','=',company_id)]
            if picking_type_id.mapped('code')[0] == 'outgoing':
                domain = [('type', '=', 'sale'),('company_id','=',company_id)]
        return domain

    journal_id = fields.Many2one('account.journal', 'Journal Destination', required=True,default=_get_journal,domain=_journal_domain)
    group = fields.Boolean(u"Regroupé par partenaire")
    dropshipping = fields.Boolean(u"Dropshipping?")
    invoice_date = fields.Date('Date Facture')

    @api.model
    def view_init(self,fields_list):
        res = super(StockInvoiceOnshipping, self).view_init(fields_list)
        pick_obj = self.env['stock.picking']
        active_ids = self.env.context.get('active_ids')
        pick_ids = pick_obj.browse(active_ids)
        if len(pick_ids.mapped('company_id')) > 1:
            raise UserError("Les réceptions / livraisons à facturer doivent appartenir à la même société!")
        if set(pick_ids.mapped('state')) != {'done'}:
            raise UserError("Seuls les réceptions / livraisons dans l'état prêt peuvent être facturés!")
        if len(set(pick_ids.picking_type_id.mapped('code'))) > 1:
            raise UserError("Les transferts à facturer doivent être du même type (réception ou livraison)!")
        return res

    #First button on wizard to create invoice
    def open_invoice(self):
        for data in self:
            invoices = self.create_invoice()
            #Open Invoices
            journal2type = {'sale':'out_invoice', 'purchase':'in_invoice'}
            inv_type = journal2type.get(data.journal_id.type) or 'out_invoice'
            if inv_type == "out_invoice":
                action = self.env.ref('account.action_move_out_invoice_type').read()[0]
            elif inv_type == "out_refund":
                action = self.env.ref('	account.action_move_out_refund_type').read()[0]
            elif inv_type == "in_invoice":
                action = self.env.ref('account.action_move_in_invoice_type').read()[0]
            elif inv_type == "in_refund":
                action = self.env.ref('account.action_move_in_refund_type').read()[0]
            if len(invoices) > 1:
                action['domain'] = [('id', 'in', invoices.ids)]
            elif len(invoices) == 1:
                form_view = [(self.env.ref('account.view_move_form').id, 'form')]
                if 'views' in action:
                    action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
                else:
                    action['views'] = form_view
                action['res_id'] = invoices.id
            else:
                action = {'type': 'ir.actions.act_window_close'}

            context = {
                'default_type': inv_type,
            }
            action['context'] = context
            return action

    #create invoice
    def create_invoice(self):
        for data in self:
            picking_pool = self.env['stock.picking']
            journal2type = {'sale':'out_invoice',
                            'purchase':'in_invoice'}
            inv_type = journal2type.get(data.journal_id.type) or 'out_invoice'
            self.with_context(date_inv=data.invoice_date, inv_type=inv_type)
            active_ids = self.env.context.get('active_ids')
            new_active_ids = []
            for a in self.env['stock.picking'].browse(active_ids):
                if not a.invoice_state:
                    new_active_ids.append(a.id)
                else:
                    raise UserError("Le transfert %s est déjà facturé!"%a.name)
            res = picking_pool.browse(new_active_ids).action_invoice_create(
                  journal_id=data.journal_id.id,
                  group=data.group,
                  dropshipping=data.dropshipping,
                  type=inv_type,
                  date=data.invoice_date
            )
        return res

