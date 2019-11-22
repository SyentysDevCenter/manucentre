# -*- coding: utf-8 -*-

from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = "account.move"

    picking_ids = fields.Many2many('stock.picking', string='BL')