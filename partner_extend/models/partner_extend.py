from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    hunting_licence_number = fields.Char(string='Permis de chasse')
    hunting_licence_date = fields.Date(string=u'Date délivrance')
    hunting_licence_validity = fields.Char(string=u'Validité Permis de chasse')
    hunting_oncfs = fields.Boolean(string=('ONCFS'))
    hunting_state = fields.Many2one(comodel_name="res.country.state",
                                    string=(u"Préfecture d'obtention permis de chasse"))

    # Shooting is different from hunting
    shooting_licence = fields.Char(string='Licence de Tir')
    shooting_licence_validity = fields.Char(string=u'Validité de la licence de Tir')
    shooting_club_number = fields.Char(string=u"Numéro du Club de Tir")
    shooting_club_name = fields.Char(string="Nom du club de Tir")

    # Shooting is different from hunting
    balltrap_licence = fields.Char(string='Licence de BallTrap')
    balltrap_licence_validity = fields.Char(string=u'Validité de la licence de Ball trap')
    balltrap_club_number = fields.Char(string=u"Numéro du Club Balltrap")
    balltrap_club_name = fields.Char(string="Nom du club Balltrap")