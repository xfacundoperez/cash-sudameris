# -*- coding: utf-8 -*-
import requests
import json
from odoo import http
from odoo.http import request

import logging
_logger = logging.getLogger(__name__)

baseUrl = 'https://dev.sudameris.com.py/api-ext/michi-auth-sudameris'
deviceIdRequestUrl = baseUrl + '/devices/new-from-ua'
authRequestUrlUser = baseUrl + '/auth/session'
authRequestUrlOperator = baseUrl + '/operator-auth/session'


class BM_OfficialSalary_MichiAuth(http.Controller):
    @http.route('/michi_auth_request_device_id', type="json", auth='public')
    def michi_auth_request_device_id(self, **kwargs):
        try:
            d = json.dumps(kwargs)
            h = request.httprequest.headers
            r = requests.post(deviceIdRequestUrl, data=d, headers=h, verify=False)
            response = json.loads(r.content)
            _logger.debug(['device_id', response])
            return {'status': r.status_code, 'response': response, 'message': 'Success'}
        except:
            return {'status': 500, 'response': False, 'message': 'Success'}

    @http.route('/michi_auth_user_login', type="json", auth='public')
    def michi_auth_user_login(self, **kwargs):
        try:
            d = json.dumps(kwargs)
            h = request.httprequest.headers
            r = requests.post(authRequestUrlUser, data=d, headers=h, verify=False)
            response = json.loads(r.content)
            _logger.debug(['user_login', response])
            return {'status': r.status_code, 'response': response, 'message': 'Success'}
        except:
            return {'status': 500, 'response': False, 'message': 'Success'}

    @http.route('/michi_auth_operator_login', type="json", auth='public')
    def michi_auth_operator_login(self, **kwargs):
        try:
            d = json.dumps(kwargs)
            h = request.httprequest.headers
            r = requests.post(authRequestUrlOperator, data=d, headers=h, verify=False)
            response = json.loads(r.content)
            _logger.debug(['operator_login', response])
            return {'status': r.status_code, 'response': response, 'message': 'Success'}
        except:
            return {'status': 500, 'response': False, 'message': 'Success'}
