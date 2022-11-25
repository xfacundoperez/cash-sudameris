# -*- coding: utf-8 -*-
from odoo import api, models, fields, _
from odoo.exceptions import UserError


class BM_OfficialSalary_Wizard(models.TransientModel):
    _name = "bm.official.salary.wizard"
    _description = "Official Salary Wizard"

    message = fields.Text(readonly=True, store=False)


class BMOfficialSalaryPaymentReasonWizard(models.TransientModel):
    """ A wizard to manage the change of users' passwords. """
    _name = "bm.official.salary.payment.reason.wizard"
    _description = "Official Salary Payment Reason Wizard"

    def _default_payment_ids(self):
        payment_ids = self._context.get('payment_ids') or []
        return [
            (0, 0, {'payment_id': payment.id, 'official_id': payment.official.id})
            for payment in self.env['bm.official.salary'].browse(payment_ids)
        ]

    payment_ids = fields.One2many(
        'bm.official.salary.payment.reason', 'wizard_id', string='Pagos', default=_default_payment_ids)

    def save_reason_button(self):
        self.ensure_one()
        self.payment_ids.save_reason_button()
        return {'type': 'ir.actions.act_window_close'}

    # @api.model
    # def create(self, vals):
    #    for line in vals['payment_ids']:
    #        if line[2]['payment_reason'] == False:
    #            raise UserError(
    #                'Debe completar los motivos de todos los funcionarios en la lista')
    #    return super(BMOfficialSalaryPaymentReasonWizard, self).create(vals)


class BMOfficialSalaryPaymentReason(models.TransientModel):
    """ A model to configure users in the change password wizard. """
    _name = 'bm.official.salary.payment.reason'
    _description = 'Official Salary Payment Reason'

    wizard_id = fields.Many2one(
        'bm.official.salary.payment.reason.wizard', string='Wizard', required=True, ondelete='cascade')
    payment_id = fields.Many2one('bm.official.salary', string='Pago',
                                 required=True, ondelete='cascade')
    official_id = fields.Many2one('bm.official', string='Funcionario')
    payment_reason = fields.Char(string='Motivo', default='')

    def save_reason_button(self):
        for line in self:
            line.payment_id.write({
                'payment_reason': line.payment_reason,
                'state': 'aproved' if (line.payment_reason) else 'draft'
            })
