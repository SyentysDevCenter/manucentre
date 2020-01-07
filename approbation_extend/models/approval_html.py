# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ApprovalCategory(models.Model):
    _inherit = 'approval.category'

    approbation = fields.Html('Approbation')
