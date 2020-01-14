# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    formulaire = fields.Html('Formulaire')


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'


    formulaire = fields.Html('Formulaire')

    @api.onchange('category_id', 'request_owner_id')
    def _onchange_category_id(self):
        super(ApprovalRequest, self)._onchange_category_id()
        if self.category_id.formulaire:
            self.formulaire = self.category_id.formulaire
