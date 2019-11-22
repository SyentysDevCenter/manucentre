# -*- coding: utf-8 -*-

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    order_policy = fields.Selection(selection=(
                                              ('picking', u'Basé sur bon de livraison'),
                                              ('prepaid', 'Avant la livraison'),
                                              ), string='Créer facture', required=True, readonly=True,states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},default='picking')