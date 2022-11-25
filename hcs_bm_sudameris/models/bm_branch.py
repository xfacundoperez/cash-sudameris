# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class BM_Branchs(models.Model):
    _name = "bm.branch"
    _description = "Sucursales"

    name = fields.Char(string='Nombre de la sucursal', required=True)
    code = fields.Char(string='Código de la sucursal', required=True)
    # Agregar campo Entrega ó Normal: Canelia y los que empiezan con CAC

    _sql_constraints = [
        ('branch_code_uniq', 'unique(code)',
         'No puden existir 2 sucursales con el mismo código'),
    ]
