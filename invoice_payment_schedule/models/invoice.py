from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class Invoice(models.Model):
    _inherit = 'account.move'

    payment_ids = fields.Many2many('account.payment', string='Paiements')
