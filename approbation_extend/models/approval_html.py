# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    approbation = fields.Html('Approbation')
