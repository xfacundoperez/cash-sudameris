# -*- coding: utf-8 -*- | , api, _
from odoo import models, fields


class BM_Products(models.Model):
    _name = 'bm.product'
    _description = 'Tabla de productos'

    name = fields.Char(index=True)
    product_type = fields.Selection([
        ('producto', 'Producto'),
        ('kit', 'Welcome Kit')], string="Tipo de producto", default='producto', store=True, required=True)
    parent_id = fields.Many2one('bm.product', index=True, ondelete='cascade')
    child_ids = fields.Many2many(comodel_name='bm.product',
                                 relation='bm_product_rel',
                                 column1='parent_id',
                                 column2='id',
                                 string='Productos del kit',
                                 domain="[('product_type', '=', 'producto')]")
    minimum_salary = fields.Integer(string="Salario minimo", default='0')
