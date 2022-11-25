# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import Session
import requests
import json

import logging
_logger = logging.getLogger(__name__)


class BM_OfficialSalary_Main(http.Controller):
    def get_user_companies(self, odoo_company_ids, login_companies=None):
        arr_company = []
        odoo_companies = request.env['res.company'].sudo()
        # Si obtengo lista de compañias al momento de hacer login, las busco y verifico que existan dentro de las company_ids
        if login_companies:
            for login_bantotal_account in login_companies:
                # API para obtener el ID de la compañia
                service_response = request.env['bm.official'].ws_consulta_cuenta_servicio(
                    login_bantotal_account)
                _logger.info(['ws_consulta_cuenta_servicio', {
                    'ok': service_response['ok'],
                    'name': service_response['data']['DesContrato'],
                    'company_code': service_response['data']['NroContrato'],
                    'bantotal_account': login_bantotal_account,
                    'accounts': service_response['data']['Datos']['sBTCuenta_Lista']
                }])

                if service_response['ok']:
                    vals = {
                        'name': service_response['data']['DesContrato'],
                        'company_code': service_response['data']['NroContrato'],
                        'bantotal_account': login_bantotal_account,
                        'accounts': service_response['data']['Datos']['sBTCuenta_Lista']
                    }
                    _logger.info(
                        ['ws_consulta_cuenta_servicio_vals', {'vals': vals}])
                    _logger.info(['ws_consulta_cuenta_servicio_odoo_companies', {
                                 'odoo_companies': odoo_companies}])
                    # Busco la empresa dentro de odoo
                    login_company = odoo_companies.search(
                        [('bantotal_account', '=', login_bantotal_account)])
                    _logger.info(['ws_consulta_cuenta_servicio_login_company', {
                                 'login_company': login_company}])

                    # Si no existe, la creo
                    if not login_company:
                        # Verifico que la empresa no esté cargada previamente sin bantotal_account
                        odoo_company_exist = odoo_companies.search(
                            [('company_code', '=', vals['company_code'])])
                        _logger.info(['ws_consulta_cuenta_servicio', {
                                     'odoo_company_exist': odoo_company_exist}])
                        if odoo_company_exist:
                            # Actualizo los datos de la empresa
                            if odoo_company_exist['name'] != vals['name']:
                                odoo_company_exist['name'] = vals['name']
                            if odoo_company_exist['company_code'] != vals['company_code']:
                                odoo_company_exist['company_code'] = vals['company_code']
                            if odoo_company_exist['bantotal_account'] != vals['bantotal_account']:
                                odoo_company_exist['bantotal_account'] = vals['bantotal_account']
                            _logger.info(['ws_consulta_cuenta_servicio', {
                                         'odoo_company_exist_if': odoo_company_exist}])
                        else:
                            # Creo la compañia
                            odoo_company_exist = odoo_companies.create({
                                'name': vals['name'],
                                'company_code': vals['company_code'],
                                'bantotal_account': vals['bantotal_account']
                            })
                            _logger.info(['ws_consulta_cuenta_servicio', {
                                         'odoo_company_exist_else': vals}])

                        _logger.info(['ws_consulta_cuenta_servicio', {
                                     'odoo_company_exist': odoo_company_exist}])
                        # Agrego la empresa a la lista de compañias
                        arr_company.append(odoo_company_exist.id)
                    else:
                        # Actualizo los datos de la empresa
                        _logger.info(['ws_consulta_cuenta_servicio_else', {
                                     'login_company': login_company}])
                        if login_company['name'] != vals['name']:
                            login_company['name'] = vals['name']
                        if login_company['company_code'] != vals['company_code']:
                            login_company['company_code'] = vals['company_code']
                        if login_company['bantotal_account'] != vals['bantotal_account']:
                            login_company['bantotal_account'] = vals['bantotal_account']
                        # Agrego la empresa a la lista de compañias
                        arr_company.append(login_company.id)
                        _logger.info(['ws_consulta_cuenta_servicio_else', {
                                     'arr_company': arr_company}])

                    _logger.info(['ws_consulta_cuenta_servicio',
                                 {'arr_company': arr_company}])

                    # Busco las cuentas asociadas a la compañia
                    odoo_company_accounts = request.env['bm.company.account'].sudo(
                    )
                    company_account_ids = []

                    for account in vals['accounts']:
                        # Verifico que la cuenta tenga el permiso PAGO DE SALARIOS
                        allowed_account = False

                        _logger.info(['ws_consulta_cuenta_servicio', {
                                     'account_servicio_lista': account['Servicio']['sBTCuenta.Lista.Servicio']}])

                        for service in account['Servicio']['sBTCuenta.Lista.Servicio']:
                            if service['Codigo'] == '101':
                                allowed_account = True
                                break
                        # Si tiene el permiso, verifico que exista
                        if allowed_account:
                            current_account = odoo_company_accounts.search(['&', '&',
                                                                            ('account', '=',
                                                                             account['Cuenta']),
                                                                            ('module', '=',
                                                                             account['Modulo']),
                                                                            ('currency_type', '=', account['Moneda'])])
                            _moneda = account['Moneda'] if (
                                account['Moneda'] in ['6900', '62', '1']) else None
                            # Si no existe la creo, sino la actualizo
                            if not current_account:
                                new_company_account = current_account.create({
                                    'account': account['Cuenta'],
                                    'module': account['Modulo'],
                                    'currency_type': _moneda,
                                    'branch_id': request.env['bm.branch'].search([
                                        ('code', '=', account['Sucursal'])]).id,
                                })
                                company_account_ids.append(
                                    new_company_account.id)
                            else:
                                current_account.write({
                                    'account': account['Cuenta'],
                                    'module': account['Modulo'],
                                    'currency_type': _moneda,
                                    'branch_id': request.env['bm.branch'].search([
                                        ('code', '=', account['Sucursal'])]).id,
                                })
                                company_account_ids.append(current_account.id)

                        _logger.info(['ws_consulta_cuenta_servicio', {
                                     'company_account_ids': company_account_ids}])

                    # Sobre escribo las cuentas a la compañia
                    login_company.search([('id', '=', login_company['id'])]).write({
                        'account_ids': company_account_ids,
                    })
                else:
                    _logger.error(['ws_consulta_cuenta_servicio', {
                        'error': 'No se obtuvo el contrato para la cuenta {}'.format(login_bantotal_account),
                        'mensaje': service_response['message']
                    }
                    ])

        # Busco las compañias obtenidas por odoo_company_ids
        for odoo_company_id in odoo_company_ids:
            odoo_company = odoo_companies.search(
                [('id', '=', odoo_company_id)])
            arr_company.append(odoo_company.id)
        return arr_company

    # Obtener información de un usuario
    @http.route('/bm_get_user_info', type="json", auth='public')
    def bm_get_user_info(self, **kwargs):
        user_info = None
        status = False
        # Hardcoded user
        kwargs['login'] = 4332768
        if request.jsonrequest:
            for user in request.env['res.users'].sudo().search([('login', '=', kwargs['login'])]):
                user_info = {
                    'id': user.id,
                    'name': user.name,
                    'company_ids': user.company_ids.ids,
                }
            status = True
        return {'status': status, 'response': user_info}

    # Chequea si el usuario existe, si las empresas existen, sino lo crea y asigna las mismas al usuario
    @http.route('/bm_check_user_login', type="json", auth='public')
    def bm_check_user_login(self, **kwargs):
        result = {
            'success': False,
            'id': None,
            'companies': None,
            'password': ''
        }

        if request.jsonrequest:
            try:
                # Si existe el usuario, lo creo
                if not kwargs['odooUser']:
                    vals = {
                        'name': kwargs['loginUser']['fullName'],
                        'login': kwargs['loginUser']['login'],
                        # Password del usuario
                        'password': kwargs['loginUser']['subjectId'],
                    }
                    new_user = request.env['res.users'].sudo().create(vals)
                    user_info = {
                        'id': new_user.id,
                        'name': new_user.name,
                        'company_ids': new_user.company_ids.ids
                    }
                else:
                    user_info = kwargs['odooUser']

                odoo_companies = []  # Compañias que obtengo desde odoo
                for odoo_company_id in user_info['company_ids']:
                    odoo_companies.append(odoo_company_id)
                # Compañias que tengo desde login
                login_companies = kwargs['loginUser']['additionalInfo']['BantotalAccountsLimits']

                _logger.info(['bm_check_user_login', {
                             'login_companies': login_companies}])

                # Busco las empresas por compañias
                user_companies = self.get_user_companies(
                    odoo_companies, login_companies)
                result['companies'] = user_companies
                user_info['company_ids'] = request.env['res.company'].sudo().search(
                    ['&', ('id', '!=', 1), ('id', 'in', user_companies)])

                _logger.info(['bm_check_user_login', {
                             'user_companies': user_companies}])

                # Fix password_policy
                result['password'] = self.generate_password_policy(user_info['company_ids'][0])
                # Sobre escribo la información de las empresas al usuario
                request.env['res.users'].browse(user_info['id']).sudo().write({
                    'password': result['password'],
                    'company_ids': user_info['company_ids'],
                    'company_id': user_info['company_ids'][0]
                })

                result['success'] = True
                result['id'] = user_info['id']
                return result
            except:
                return result

    def generate_password_policy(self, company_id):
        import string
        import random

        # Password to return
        password = ''        

        # Set the min lower chars
        for i in range(company_id.password_lower):
            password += random.choice(string.ascii_lowercase)

        # Set the min upper chars
        for i in range(company_id.password_upper):
            password += random.choice(string.ascii_uppercase)

        # Set the min numeric chars
        for i in range(company_id.password_numeric):
            password += random.choice(string.digits)

        # Set the min special chars
        for i in range(company_id.password_special):
            password += random.choice("!@#$%^&*()")
            #password += random.choice(string.punctuation)

        _logger.info(['generate_password_policy: Ready', password])
        # If need more security, complete password with lowercase
        while (len(password) < company_id.password_length):
            _logger.info(['generate_password_policy', 'Añadiendo caracter'])
            password += random.choice(string.ascii_lowercase)

        ## shuffling the resultant password and rejoin
        password = list(password)
        random.shuffle(password)
        password = "".join(password)
        _logger.info(['generate_password_policy: OK', password])
        return password

    # Obtener información de un usuario
    @http.route('/bm_write_session_data', type="json", auth='public')
    def bm_write_session_data(self, *args, **kwargs):
        if request.jsonrequest:
            for user in request.env['res.users'].sudo().search([('id', '=', kwargs['user_id'])]):
                user.sudo().write({
                    'password': kwargs['password'],
                    'bm_api_key': kwargs['ApiKey'],
                    'bm_access_token': kwargs['AccessToken'],
                })
        return {'success': True, 'message': 'Success'}


class BM_SessionLogout(Session):

    @http.route('/web/session/logout', type='http', auth="none", website=True, multilang=False, sitemap=False)
    def bm_logout(self):
        baseUrl = 'https://dev.sudameris.com.py/api-ext/michi-auth-sudameris'
        authRequestUrlUser = baseUrl + '/auth/session'
        for user in request.env['res.users'].sudo().search([('id', '=', request._context['uid'])]):
            if 'X-RshkMichi-AccessToken' in request.httprequest.cookies.keys():
                u = authRequestUrlUser + "/" + \
                    request.httprequest.cookies['X-RshkMichi-AccessToken']
                h = {'X-RshkMichi-ApiKey': user['bm_api_key']}
                r = requests.delete(u, headers=h)
                _logger.debug(['RESPONSE_LOGOUT', json.loads(r.content)])
            # Borro el api_key u access_token
            user['bm_api_key'] = ''
            user['bm_access_token'] = ''

        return super().logout(redirect='/web/login#clean')
