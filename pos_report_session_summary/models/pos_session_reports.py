# -*- coding: utf-8 -*-

from odoo import api, fields, models, tools, _


class ReportSessionSummary(models.AbstractModel):

    _name = 'report.pos_report_session_summary.pos_report_sessionsummary'
    _description = 'Point of Sale session summary reports'

    @api.model
    def get_session_details(self, session_ids=False):

        if session_ids:

            session = self.env['pos.session'].browse(session_ids)
            orders = session.order_ids

            # get taxes total group by taxes type
            total = 0.0
            products_sold = {}
            taxes = {}
            for order in orders:
                total += order.amount_total
                currency = order.session_id.currency_id

                for line in order.lines:
                    key = (line.product_id, line.price_unit, line.discount)
                    products_sold.setdefault(key, 0.0)
                    products_sold[key] += line.qty

                    if line.tax_ids_after_fiscal_position:
                        line_taxes = line.tax_ids_after_fiscal_position.compute_all(line.price_unit * (1-(line.discount or 0.0)/100.0), currency, line.qty, product=line.product_id, partner=line.order_id.partner_id or False)
                        for tax in line_taxes['taxes']:
                            taxes.setdefault(tax['id'], {'name': tax['name'], 'tax_amount':0.0, 'base_amount':0.0})
                            taxes[tax['id']]['tax_amount'] += tax['amount']
                            taxes[tax['id']]['base_amount'] += tax['base']
                    else:
                        taxes.setdefault(0, {'name': _('No Taxes'), 'tax_amount':0.0, 'base_amount':0.0})
                        taxes[0]['base_amount'] += line.price_subtotal_incl

            tax_total = 0.00
            for line in list(taxes.values()):
                tax_total += line['tax_amount']

            # prepare for a summary of pos session
            pos_payment_by_method_ids = session.pos_payment_by_method_ids.ids
            if pos_payment_by_method_ids:
                self.env.cr.execute("""
			    		select ppm.name, ppmt.type, ppmt.amount 
			    		from pos_payment_method_type as ppmt, pos_payment_method as ppm
			    		where ppmt.id in %s
			    		and ppmt.pos_payment_id = ppm.id;
                            """, (tuple(pos_payment_by_method_ids),))
                pos_payments_by_method = self.env.cr.dictfetchall()
            else:
                pos_payments_by_method = []

            # tbd
            payment_ids = self.env["pos.payment"].search([('pos_order_id', 'in', orders.ids)]).ids
            if payment_ids:
                self.env.cr.execute("""
                    SELECT method.name, sum(amount) total
                    FROM pos_payment AS payment,
                         pos_payment_method AS method
                    WHERE payment.payment_method_id = method.id
                        AND payment.id IN %s
                    GROUP BY method.name
                """, (tuple(payment_ids),))
                payments = self.env.cr.dictfetchall()
            else:
                payments = []

            # payments BO
            self.env.cr.execute("""
                        select ap.payment_date, ap.name, ps.name as pos_session_id, rp.name as partner_id, rpu.name as create_uid, ap.amount  
				        from account_payment as ap, pos_session as ps, res_partner as rp, res_users as ru, res_partner as rpu
				        where pos_session_id =%s
				        and ap.pos_session_id = ps.id
				        and ap.partner_id = rp.id
				        and ap.create_uid = ru.id
				        and ru.partner_id = rpu.id ;
            """, (session.id,))
            payments_bo = self.env.cr.dictfetchall()

            # all payments details
            self.env.cr.execute("""
                    select payment.payment_date, payment.pos_session, payment.amount, payment.payment_method, payment.pos_reference, rp.name, payment.user_id from (
					select pp.payment_date, ps.name as pos_session, pp.amount, ppm.name as payment_method, po.pos_reference, po.partner_id, rp.name as user_id
					from pos_payment as pp, pos_session as ps, pos_payment_method as ppm, pos_order as po, res_users as ru, res_partner as rp
					where pp.session_id = %s
					and pp.session_id = ps.id
					and pp.payment_method_id = ppm.id
					and pp.pos_order_id = po.id
					and po.user_id = ru.id
					and ru.partner_id = rp.id
					)as payment
					LEFT JOIN res_partner as rp 
					ON payment.partner_id = rp.id
					;
                        """, (session.id,))
            pos_payments = self.env.cr.dictfetchall()

            return {
                'payments': payments,
                'taxes': list(taxes.values()),
                'taxes_total': tax_total,
                'session_name': session.name,
                'session_user': session.user_id.name,
                'session_start': session.start_at,
                'session_stop': session.stop_at,
                'total_untaxed': total - tax_total,
                'total_all': total,
                'pos_payments': pos_payments,
                'payments_bo': payments_bo,
                'pos_payments_by_method': pos_payments_by_method
            }

    @api.model
    def _get_report_values(self, docids, data=None):
        data = dict(data or {})
        data.update(self.get_session_details(docids))
        return data
