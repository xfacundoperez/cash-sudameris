# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BM_OfficialSalary(models.Model):
    _name = 'bm.official.salary'
    _description = 'Movimiento de salario del funcionaro'
    _rec_name = 'official'

    @api.depends('amount_to_pay', 'official_gross_salary')
    def _compute_amount_to_pay(self):
        for rec in self:
            rec.amount_to_pay = rec.official_gross_salary

    @api.depends('payment_reason', 'last_payment_date')
    def _compute_payment_reason(self):
        for rec in self:
            if rec.last_payment_date:
                if (datetime.now().date() - rec.last_payment_date).days > 35 and not rec.payment_reason:
                    rec.state = 'draft'
                else:
                    rec.state = 'aproved'

    official = fields.Many2one('bm.official', 'Funcionario')
    official_identification_id = fields.Char(
        string='Nº identificación', related='official.identification_id', readonly=True)
    official_company_id = fields.Many2one(
        'res.company', related='official.company_id', readonly=True)
    official_currency_type = fields.Selection([
        ('6900', 'Guaraníes'),
        ('1', 'Dólares Americanos')], strsng="Moneda", related='official.currency_type', readonly=True)
    official_gross_salary = fields.Float("Salario del funcionario", digits=(
        18, 2), related='official.gross_salary', readonly=True)
    amount_to_pay = fields.Float(string="Salario a pagar", digits=(
        18, 2), compute=_compute_amount_to_pay, store=True)
    charge_type = fields.Selection([
        ('1', 'Sueldo'),
        ('2', 'Aguinaldo'),
        ('3', 'Anticipo de Sueldo'),
        ('4', 'Otras Remuneraciones'),
        ('7', 'Acreditación Tarjeta Prepaga'),
        ('8', 'Pago de Licencias')], string="Tipo de Cobro", default="1")
    payment_date = fields.Date(
        string="Fecha de pago", default=lambda s: fields.Date.context_today(s))
    last_payment_date = fields.Date(
        string="Fecha de ultimo pago")
    payment_mode = fields.Selection([
        ('20', 'Cta. Cte'),
        ('21', 'Caja de Ahorro')], string="Modalidad de pago", default="21")
    payment_reason = fields.Char(
        string="Motivo de no cobro", compute="_compute_payment_reason", store=True)
    operation_type = fields.Char(string="Tipo de Operación")
    operation_code = fields.Char(string="Operación")
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda self: self.env.company)
    suboperacion_code = fields.Char(string="Suboperación")
    reference = fields.Char(string="Referencia")
    gx_exist = fields.Selection([
        ('S', 'Es Payroll'),
        ('N', 'No es Payroll'),
        ('A', 'Pendiente a cobrar')
    ], string="Clasificación Payroll")
    state = fields.Selection([
        ('draft', 'Preliquidación'),
        ('aproved', 'Aprobado'),
        ('done', 'Procesado')], string="Estado", default='draft')
    movement_id = fields.Many2one('bm.official.salary.history')

    def show_message(self, title, message):
        return {
            'name': title,
            'type': 'ir.actions.act_window',
            'res_model': 'bm.official.salary.wizard',
            'view_mode': 'form',
            'context': {'default_message': message},
            'target': 'new'
        }

    def show_warning(self, title, message):
        return {
            'warning': {
                'title': title,
                'message': message,
            },
        }

    def action_aprove_salary_movement(self):
        """# Action: Aprobar
        Accion relacionada: Control Cliente Payroll(funcionario seleccionado)
        """
        result = {
            'message': '',
            'count_ok': 0,
            'errors': {
                'salary_payment_reson': []
            },
            'vbc': None
        }

        for official_salary in self.env['bm.official.salary'].browse(self._context.get('active_ids')) or self:
            if official_salary.state == 'draft':
                official_salary.state = 'aproved'
                result['count_ok'] += 1

            service_result = official_salary.official.ws_control_cliente_payroll(
                official_salary.official)

            if service_result['data']['FcUltCobro'] not in ['0000-00-00', '']:
                official_salary.gx_exist = service_result['data']['GxExiste']
                # Verifico que el funcionario no tenga registros en los 30 días
                last_payment_date = datetime.strptime(
                    service_result['data']['FcUltCobro'], '%Y-%m-%d').date()

                diference_days = (datetime.now().date() -
                                  last_payment_date).days

                if diference_days > 35 and not official_salary.payment_reason:
                    result['errors']['salary_payment_reson'].append(
                        official_salary.id)

                official_salary.last_payment_date = last_payment_date

        if result['errors']['salary_payment_reson']:
            return {
                'name': 'Aprobar registro',
                'type': 'ir.actions.act_window',
                'binding_model': 'bm.official.salary',
                'res_model': 'bm.official.salary.payment.reason.wizard',
                'view_mode': 'form',
                'context': {
                    'active_ids': self._context.get('active_ids'),
                    'payment_ids': result['errors']['salary_payment_reson'],
                },
                'target': 'new'
            }

        # Aprobar movimientos
        result['message'] = 'Se aprobaron {} movimientos\n\n'.format(
            result['count_ok'])

        return self.show_message('Remitir al Banco', result['message'])

    def action_reset(self):
        for official_salary in self.env['bm.official.salary'].browse(self._context.get('active_ids')) or self:
            official_salary.state = 'draft'
            official_salary.last_payment_date = None
            official_salary.payment_reason = None

    def create_file_txt(self, sac='1'):
        # Los registros que están aprobados, los seteo en proceso
        for official_salary in self.env['bm.official.salary'].browse(self._context.get('active_ids')) or self:
            if official_salary.state == 'aproved':
                official_salary.state = 'done'
        # Obtengo solo los ID de los que están en proceso y si hay alguno, genero el archivo de pago
        _ids = self.search(['&', ('id', 'in', self._context.get(
            'active_ids')), ('state', 'in', ['aproved', 'done'])]).ids
        if _ids:
            return {
                'type': 'ir.actions.act_url',
                'url': '/web/binary_file/create_file_txt?ids={}&sac={}&code={}'.format(','.join([str(_id) for _id in _ids]), sac, self.env.user.company_id.company_code),
                'target': 'self'
            }
        else:
            return self.show_message('Generar Pago', 'No se generó ningun pago')


class BM_OfficialSalaryHistory(models.Model):
    _name = 'bm.official.salary.history'
    _description = 'Historial de Movimiento de salario'

    def _compute_name(self):
        for rec in self:
            rec.name = "Movimiento N°{}".format(rec.id)

    name = fields.Char(compute="_compute_name")
    official_salary_ids = fields.Many2many(
        'bm.official.salary', 'official_salary_rel', 'official_id')

    # def create_file_txt(self, last_movement=None):
    #  return True
    #  if not last_movement:
    #    last_movement = self.env['bm.official.salary.history'].search('id', 'in', self.env._context.get('active_ids'))
