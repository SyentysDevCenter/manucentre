from odoo import api, fields, models


class Product(models.Model):
    _inherit = 'product.product'

    old_id = fields.Integer(string='Old id', readonly=True)
    probleme = fields.Char()

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    old_id = fields.Integer(string='Old id', readonly=True)

class ProductCateg(models.Model):
    _inherit = 'product.category'

    old_id = fields.Integer(string='Old id', readonly=True)

    def compute_complete_name(self):
        self._compute_complete_name()


class ResPartner(models.Model):
    _inherit = 'res.partner'

    old_id = fields.Integer(string='Old id', readonly=True)


class StockProductLot(models.Model):
    _inherit = 'stock.production.lot'

    old_id = fields.Integer(string='Old id', readonly=True)


class ProductSupplierinfo(models.Model):
    _inherit = 'product.supplierinfo'

    old_id = fields.Integer(string='Old id', readonly=True)


class ProductBrand(models.Model):
    _inherit = 'product.brand'

    old_id = fields.Integer(string='Old id', readonly=True)


class UomUom(models.Model):
    _inherit = 'uom.uom'

    old_id = fields.Integer(string='Old id', readonly=False)


class ResCompany(models.Model):
    _inherit = 'res.company'

    old_id = fields.Integer(string='Old id', readonly=True)


class ResCountryState(models.Model):
    _inherit = 'res.country.state'

    old_id = fields.Integer(string='Old id', readonly=False)


class ProductTags(models.Model):
    _inherit = 'product.tags'

    old_id = fields.Integer(string='Old id', readonly=False)


class ProductAttribute(models.Model):
    _inherit = 'product.attribute'

    old_id = fields.Integer(string='Old id', readonly=False)

class Account(models.Model):
    _inherit = 'account.account'

    old_id = fields.Integer(string='Old id', readonly=False)


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    old_id = fields.Integer(string='Old id', readonly=False)

class ProductTemplateAttributeLine(models.Model):
    _inherit = 'product.template.attribute.line'

    old_id = fields.Integer(string='Old id', readonly=False)


