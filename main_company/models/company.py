from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError

class ResCompany(models.Model):
    _inherit = 'res.company'

    main_company = fields.Boolean('Centrale')

    @api.constrains('main_company')
    def _verify_pin(self):
        for company in self:
            if  company.main_company and self.search([('main_company','=',True),('id','!=',company.id)]):
                raise ValidationError("Une seule société peut être désignée comme étant la centrale!.")