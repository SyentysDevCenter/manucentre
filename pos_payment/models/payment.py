# -*- coding: utf-8 -*-

from odoo import api, fields, models

class POSPayment(models.Model):
    _name = 'pos.payment.method.type'

    pos_payment_id = fields.Many2one('pos.payment.method', string='Pos payment')
    amount = fields.Float('Montant')
    type = fields.Selection(selection=[('pos', 'POS'), ('account', 'Paiement BO')], string='Type')


class PosPaymentMethod(models.Model):
    _inherit = 'pos.payment.method'

    pay_method_id = fields.Many2one('account.payment.method',string='Méthode de payment',domain="[('payment_type','=','inbound')]")

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def _get_pos_session(self):
        pos_session = self.env['pos.session'].search([('state','in',['opened','opening_control','closing_control']),('company_id','=',self.env.company.id)])
        if pos_session:
            return pos_session
        else:
            return False

    @api.onchange('payment_method_id')
    def onchange_payment_method_id(self):
        if self.payment_method_id:
            pos_payment_id = self.env['pos.payment.method'].search([('pay_method_id','=',self.payment_method_id.id),('company_id','=',self.company_id.id)],limit=1)
            if pos_payment_id:
                self.pos_payment_id = pos_payment_id

    pos_payment_id = fields.Many2one('pos.payment.method',string='Pos payment',domain="[('company_id','=',company_id)]")
    pos_session_id = fields.Many2one('pos.session',string='POS session',default=_get_pos_session)

class PosSession(models.Model):
    _inherit = 'pos.session'

    account_payment_ids = fields.One2many('account.payment','pos_session_id','Paiements BO')
    total_account_payments_amount = fields.Float(compute='_compute_total_account_payments_amount', string='Total Payments Amount BO')

    @api.depends('account_payment_ids.amount')
    def _compute_total_account_payments_amount(self):
        for session in self:
            session.total_account_payments_amount = sum(session.account_payment_ids.mapped('amount'))

    def action_show_account_payments_list(self):
        return {
            'name': ('Paiments BO'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.payment',
            'view_mode': 'tree,form',
            'domain': [('pos_session_id', '=', self.id)],
        }

    pos_payment_by_method_ids = fields.Many2many('pos.payment.method.type',compute='get_payments')

    def get_payments(self):
        pay_obj = self.env['pos.payment.method.type']
        for rec in self:
            pay_ids = self.sudo().env['pos.payment'].read_group([('session_id', '=', rec.id)], ['payment_method_id', 'amount'], ['payment_method_id'])
            for pay in pay_ids:
                pay_obj |= pay_obj.sudo().create({
                    'pos_payment_id':pay['payment_method_id'][0],
                    'amount':pay['amount'],
                    'type':'pos',
                })
            account_pay_ids = self.sudo().env['account.payment'].read_group([('pos_session_id', '=', rec.id)],
                                                                ['pos_payment_id', 'amount'], ['pos_payment_id'])
            for pay in account_pay_ids:
                pay_obj |= pay_obj.sudo().create({
                    'pos_payment_id': pay['pos_payment_id'][0],
                    'amount': pay['amount'],
                    'type': 'account',
                })
            rec.pos_payment_by_method_ids = pay_obj

