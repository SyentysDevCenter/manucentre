# -*- coding: utf-8 -*-

from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    invoice_state = fields.Boolean(string='Facturé',readonly=True)

    @api.model
    def create_invoices(self,partner,pick_ids,journal_id,date,type,dropshipping):
        invoices = self.env['account.move']
        invoice_obj = self.env['account.move']
        partner_id = self.env['res.partner'].browse(partner)
        journal_obj = self.env['account.journal']
        company_id = pick_ids.mapped('company_id')
        main_company = self.env['res.company'].search([('main_company', '=', True)])
        inter_company = self.env['res.company'].search([('partner_id', '=', partner_id.id)])
        if main_company and inter_company and dropshipping:
            partner_id = main_company.partner_id
            company_id = main_company
            if pick_ids.mapped('picking_type_id').mapped('code')[0] == 'incoming':
                journals = journal_obj.search([('type', '=', 'sale'), ('company_id', '=', company_id.id)])
                journal_id = journals and journals[0] or False
                type = 'out_invoice'
            if pick_ids.mapped('picking_type_id').mapped('code')[0] == 'outgoing':
                journals = journal_obj.search([('type', '=', 'sale'), ('company_id', '=', company_id.id)])
                journal_id = journals and journals[0] or False
                type = 'out_refund'
        payment_term_id = False
        if type in ('in_invoice','in_refund'):
            payment_term_id = partner_id.with_context(force_company=company_id.id).property_supplier_payment_term_id.id
        if type in ('out_invoice','out_refund'):
            payment_term_id = partner_id.with_context(force_company=company_id.id).property_payment_term_id.id
        move_ids = pick_ids.mapped('move_ids_without_package')
        inv_line_ids = []
        for move in move_ids:
            tax_ids = []
            analytic_tag_ids = []
            analytic_account_id = False
            purchase_order_line = False
            sale_order_line = []
            price_unit = 0
            account_id = False
            if type in ('in_invoice','in_refund'):
                account_id = move.product_id.with_context(force_company=company_id.id).property_account_expense_id.id
            if type in ('out_invoice','out_refund'):
                account_id = move.product_id.with_context(force_company=company_id.id).property_account_income_id.id
            if move.purchase_line_id:
                tax_ids = move.purchase_line_id.with_context(force_company=company_id.id).taxes_id.ids
                analytic_tag_ids = move.purchase_line_id.with_context(force_company=company_id.id).analytic_tag_ids.ids
                analytic_account_id = move.purchase_line_id.with_context(force_company=company_id.id).account_analytic_id.id
                purchase_order_line = move.purchase_line_id.id
                price_unit = move.purchase_line_id.with_context(force_company=company_id.id).price_unit
            if move.sale_line_id:
                tax_ids = move.sale_line_id.with_context(force_company=company_id.id).tax_id.ids
                analytic_tag_ids = move.sale_line_id.with_context(force_company=company_id.id).analytic_tag_ids.ids
                analytic_account_id = move.sale_line_id.with_context(force_company=company_id.id).order_id.analytic_account_id.id
                price_unit = move.sale_line_id.with_context(force_company=company_id.id).price_unit
                sale_order_line = move.sale_line_id and move.sale_line_id.ids
            inv_line_ids.append((0,0,{
                'name': move.name,
                'account_id':account_id,
                'price_unit': price_unit,
                'quantity': move.quantity_done,
                'product_id': move.product_id.id,
                'product_uom_id': move.product_uom.id,
                'tax_ids': [(6, 0, tax_ids)],
                'purchase_line_id':purchase_order_line,
                'analytic_tag_ids': [(6, 0, analytic_tag_ids)],
                'analytic_account_id': analytic_account_id,
                'sale_line_ids':[(6, None, sale_order_line)],
            }))

        inv_data = {'type': type,
                    'ref':'-'.join(pick_ids.mapped('inter_proc')),
                    'invoice_date':date,
                    'journal_id':journal_id,
                    'company_id': company_id.id,
                    'invoice_origin': '-'.join(pick_ids.mapped('name')),
                    'invoice_user_id': self.env.user.id,
                    'partner_id': partner,
                    'fiscal_position_id': partner_id.with_context(force_company=company_id.id).property_account_position_id.id,
                    'partner_shipping_id': partner,
                    'currency_id': company_id.currency_id.id,
                    'invoice_payment_term_id': payment_term_id,
                    'picking_ids': [(6,0,pick_ids.mapped('id'))],
                    'invoice_line_ids': inv_line_ids,
                    }
        new_inv = invoice_obj.create(inv_data)
        invoices |= new_inv
        return invoices

    @api.model
    def action_invoice_create(self,journal_id,group,dropshipping,type,date):
        res = self.env['account.move']
        invoices_by_partner = {}
        if group:
            for pick in self:
                part_id = pick.partner_id.id
                if invoices_by_partner.get(part_id,False):
                    invoices_by_partner[part_id]|= pick
                else:
                    invoices_by_partner[part_id] = pick
            for partner in invoices_by_partner:
                res |= self.create_invoices(partner, invoices_by_partner[partner], journal_id, date, type)
                invoices_by_partner[partner].write({'invoice_state':True})
        else:
            for pick in self:
                res |= self.create_invoices(pick.partner_id.id, pick, journal_id, date, type,dropshipping)
                pick.write({'invoice_state':True})
        return res