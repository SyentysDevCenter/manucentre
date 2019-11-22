# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

JOURNAL_TYPE_MAP = {
                    ('outgoing', 'customer'): ['sale'],
                    ('incoming', 'supplier'): ['purchase'],
                    }


class StockInvoiceOnshipping(models.TransientModel):

    #Default Journal
    @api.model
    def _get_journal(self):
        journal_obj = self.env['account.journal']
        journal_type = self._get_journal_type()
        journals = journal_obj.search([('type', '=', journal_type)])
        return journals and journals[0] or False

    #Get Journal Type
    @api.model
    def _get_journal_type(self):
        res_ids = self.env.context.get('active_ids')
        pick_obj = self.env['stock.picking']
        pickings = pick_obj.browse(res_ids)
        picking_type_id = pickings.mapped('picking_type_id')
        if picking_type_id.mapped('code')[0] == 'incoming':
            return 'purchase'
        elif picking_type_id.mapped('code')[0] == 'outgoing':
            return 'sale'
        else:
            raise UserError("Seules les livraisons / réceptions peuvent être facturés!")

    _name = "stock.invoice.onshipping"
    _description = "Stock Invoice Onshipping"

    journal_id = fields.Many2one('account.journal', 'Journal Destination', required=True,default=_get_journal)
    journal_type = fields.Selection(selection=(('purchase', u'Créer Facture Fournisseur'),
                                               ('sale', u'Créer Facture Client')),
                                    string='Type de journal',default=_get_journal_type)
    group = fields.Boolean(u"Regroupé par partenaire")
    refund = fields.Boolean(u"Avoir?")
    invoice_date = fields.Date('Date Facture')

    #Onchange journal type si le journal est changé
    def onchange_journal_id(self, journal_id):
        domain = {}
        value = {}
        active_id = self.env.context.get('active_id')
        if active_id:
            picking = self.env['stock.picking'].browse(active_id)
            type = picking.picking_type_id.code
            usage = picking.move_lines[0].location_id.usage if type == 'incoming' else picking.move_lines[0].location_dest_id.usage
            journal_types = JOURNAL_TYPE_MAP.get((type, usage), ['sale', 'purchase'])
            domain['journal_id'] = [('type', 'in', journal_types)]
        if journal_id:
            journal = self.env['account.journal'].browse(journal_id)
            value['journal_type'] = journal.type
        return {'value': value, 'domain': domain}

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
            inv_type = journal2type.get(data.journal_type) or 'out_invoice'
            if inv_type in ("out_invoice", "out_refund"):
                action = self.env.ref('account.action_move_out_invoice_type').read()[0]
                default_type = 'out_invoice'
            elif inv_type in ("in_invoice", "in_refund"):
                action = self.env.ref('account.action_move_in_invoice_type').read()[0]
                default_type = 'in_invoice'
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
                'default_type': default_type,
            }
            action['context'] = context
            return action

    #create invoice
    def create_invoice(self):
        for data in self:
            picking_pool = self.env['stock.picking']
            journal2type = {'sale':'out_invoice',
                            'purchase':'in_invoice'}
            inv_type = journal2type.get(data.journal_type) or 'out_invoice'
            if inv_type == 'out_invoice' and data.refund:
                inv_type = 'in_refund'
            if inv_type == 'in_invoice' and data.refund:
                inv_type = 'out_refund'
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
                  type=inv_type,
                  date=data.invoice_date
            )
        return res

