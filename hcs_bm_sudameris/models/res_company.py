from odoo import models, fields


class BMResCompany(models.Model):
    _inherit = 'res.company'

    company_code = fields.Char(
        'Código de la Empresa', required=True, default='0')
    bantotal_account = fields.Char('Cuenta Bantotal')
    branch_id = fields.Many2one(
        'bm.branch', 'Sucursal de la empresa')
    account_ids = fields.Many2many(
        'bm.company.account', 'company_account_rel', 'account_id', string='Cuentas de la compañia')

    _sql_constraints = [
        ('company_code_uniq', 'unique(company_code)',
         'No puden existir 2 empresas con el mismo código'),
    ]


class BMCompanyAccount(models.Model):
    _name = "bm.company.account"
    _description = "Tabla de cuentas de empresas"

    account = fields.Char('Cuenta')
    module = fields.Char('Modulo')
    currency_type = fields.Selection([
        ('6900', 'Guaraníes'),
        ('62', 'Moneda 62'),
        ('1', 'Dólares Americanos')], string="Tipo de moneda")
    branch_id = fields.Many2one(
        'bm.branch', 'Sucursal de la empresa')
