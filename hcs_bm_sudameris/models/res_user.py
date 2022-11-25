from odoo import models, fields


class BMResUser(models.Model):
    _inherit = 'res.users'

    bm_api_key = fields.Char('X-RshkMichi-ApiKey', default='')
    bm_access_token = fields.Char('X-RshkMichi-AccessToken', default='')