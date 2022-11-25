# -*- coding: utf-8 -*-
from odoo import api, fields, models

REJECT_REASONS = [
    ('1', 'CI ILEGIBLE O DAÑADA'),
    ('2', 'CI VENCIDA'),
    ('3', 'FALTA ANVERSO/REVERSO'),
    ('4', 'NO COINCIDE'),
    ('5', 'CEDULA ADULTERADA'),
    ('6', 'OTRO')]

CPE_STATUS = [
    ('1', 'WK PENDIENTE DE ENTREGA'),
    ('2', 'VARIACION DE FIRMA'),
    ('3', 'FALTA FIRMA FORMULARIO'),
    ('4', 'CÉDULA ILEGIBLE'),
    ('5', 'PENDIENTE DE ACTIVACION')]


class BMOfficialWizard(models.TransientModel):
    _name = "bm.official.wizard"
    _description = "BM Official Wizard"

    @api.depends('debugapibantotal')
    def _compute_debug_trace(self):
        officials = []
        debug_trace_result = ''
        for rec in self:
            if 'debug_trace' in self.env.context:
                for dt in self._context.get('debug_trace'):
                    official_name = dt[0]
                    if not official_name in dict(officials):
                        officials.append((official_name, [dt[1]]))
                    else:
                        dict(officials)[official_name].append(dt[1])
        for official in officials:
            dtmessage = ''
            for idx,dt in enumerate(official[1]):
                dtmessage += '%(id)s: %(dtm)s\n' % ({
                'id': idx,
                'dtm': dt
                })
            debug_trace_result += '%(official)s: \n%(dtm)s' % ({
                'official': official[0],
                'dtm': dtmessage
                })
        rec.debug_trace = debug_trace_result

    message = fields.Text(readonly=True, store=False)
    debug_trace = fields.Text(readonly=True, store=False, compute='_compute_debug_trace')
    debugapibantotal = fields.Boolean(readonly=True, store=False, default=lambda self: self.env.user.debugapibantotal or False)

class BMOfficialWizardRejectCAM(models.TransientModel):
    _name = 'bm.official.wizard.rejectcam'
    _description = "BM Official Wizard Rechazar CAM"

    def button_save(self):
        official = self.env['bm.official'].browse(
            self.env.context.get('active_id'))
        if self.reject_reason != '6':
            official.reject_reason = dict(
                self._fields['reject_reason'].selection).get(self.reject_reason)
        else:
            official.reject_reason = self.reject_reason_description
        official.state = 'error'

        #notify_body = 'Se rechazo el alta del Funcionario: {} ({}).<br>Motivo: {}'.format(
        #    official.name, official.identification_id, official.reject_reason)
        official.message_post(
            subject='Rechazo del funcionario',
            body=official.reject_reason
        )
        return True

    reject_reason = fields.Selection(
        REJECT_REASONS, string="Motivo de rechazo", required=True, default='1')
    reject_reason_description = fields.Text('Descripción del rechazo')


class BMOfficialWizardStatusCPE(models.TransientModel):
    _name = "bm.official.wizard.statuscpe"
    _description = "BM Official Wizard Status CPE"

    def button_save(self):
        official = self.env['bm.official'].browse(
            self.env.context.get('active_id'))
        official.reject_reason = dict(
            self._fields['cpe_status'].selection).get(self.cpe_status)
        # Agrego Pendiente de activación si viaja a payroll entregas
        if self.cpe_status == '5':
            official.state = 'pending'
            _reject_reason_desc = official.reject_reason
        else:
            # Agrego Pendiente de activación si viaja a payroll entregas
            _reject_reason_desc = 'PENDIENTE DE ACTIVACION: ' + official.reject_reason
    
        official.reject_reason = _reject_reason_desc

    cpe_status = fields.Selection(CPE_STATUS, string="Estado del funcionario")
