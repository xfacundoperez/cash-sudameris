# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta

DEPARTURE_REASONS = [('medical', 'Medica'), ('fired', 'Despido'),
                     ('resigned', 'Renuncia'), ('retired', 'Retirado')]


class BM_OfficialDeparture(models.Model):
    _name = 'bm.official.departure'
    _description = 'Licencia del funcionario'

    name = fields.Char(compute='_compute_name')
    official = fields.Many2one('bm.official', 'Funcionario')
    official_identification_id = fields.Char(
        string='Nº identificación', related='official.identification_id', readonly=True)
    departure_reason = fields.Selection(
        DEPARTURE_REASONS, string="Motivo de salida", copy=False, tracking=True, required=True, default="medical")
    departure_description = fields.Text(
        string="Salida: Información adicional", copy=False, tracking=True)
    departure_start = fields.Date(
        string="Fecha de Salida", default=lambda self: datetime.now().date(), copy=False, required=True)
    departure_end = fields.Date(string="Fecha de Retorno", copy=False)
    state = fields.Selection([
        ('active', 'Activo'),
        ('finish', 'Finalizado')],
        string="Estado", default='active')

    def write(self, vals):
        res = super(BM_OfficialDeparture, self)
        departure_limit = datetime.now() + timedelta(35)
        self.official.state = 'departured'
        if self.departure_reason == 'medical' and (self.departure_end > departure_limit.date()):
            print("SE EXEDE 35 DIAS")
        return res.write(vals)

    @api.depends('official', 'departure_reason', 'departure_end')
    def _compute_name(self):
        for official_departure in self:
            official_departure.name = '#{}: {}'.format(official_departure.id, dict(
                DEPARTURE_REASONS)[official_departure.departure_reason])
            # active by default
            official_departure.state = 'active'
            if official_departure.departure_reason == 'medical':
                # if departure_end is less from today, means is not departured
                if official_departure.departure_end < datetime.now().date():
                    official_departure.state = 'finish'

    @api.onchange('departure_reason')
    def on_change_departure_reason(self):
        if self.departure_reason == 'medical':
            self.departure_end = self._origin.departure_end
        else:
            self.departure_end = None

    def action_departure_view_report(self, sac='1'):
        # Obtengo solo los ID de los que están en proceso y si hay alguno, genero el archivo de pago
        officials = []
        for reg in self.search(['&', ('id', 'in', self._context.get('active_ids')), ('state', 'in', ['active'])]):
            officials.append(reg.official.id)
        if officials:
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/binary_file/create_departure_report?ids={}'.format(','.join([str(_id) for _id in officials])),
                'target': 'self'
            }
        else:
            return self.show_message('Informe de desvinculados', 'No se encontraron desvinculados.')
