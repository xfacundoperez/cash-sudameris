# -*- coding: utf-8 -*-
from random import randint
from odoo import fields, models


class BM_OfficialCategory(models.Model):
    _name = "bm.official.category"
    _description = "Categoria del Funcionario"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string="Nombre", required=True)
    color = fields.Integer(string='Color', default=_get_default_color)
    employee_ids = fields.Many2many(
        'bm.official', 'official_category_rel', 'category_id', 'official_id', string='Funcionarios')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "El nombre de la etiqueta ya existe!"),
    ]
