from odoo import models
from datetime import datetime
from .API.ws_base_api import BM_ApiBase

import logging
logger = logging.getLogger(__name__)


class BM_OfficialApi(models.Model):
    """Funciones relacionadas a las APIs del modelo bm.official"""
    _inherit = "bm.official"

    def init_service(self):
        self.api_service = BM_ApiBase(self.env['ir.config_parameter'].sudo())
        self.officials = self.env['bm.official'].search(
            [('id', 'in', self.env.context.get('active_ids'))]) or self
        self.result = {
            'ok': False,
            'pass': False,
            'error': False,
            'message': '',
            'debug': '',
            'data': {}
        }

    def ws_valida_base_confiable(self, official):
        """
        # API: Valida base confiable
        - Valido que el funcionario exista en la base de datos de movimientos bancarios

        Esta API no se utiliza ya que es una base de datos donde la persona puede existir pero no
        dentro de la base de datos del banco.

        Si se decide usar, se deberia re analizar la funcion
        """
        self.init_service()

        if not official.reliable_base:  # Si no fue consultado
            service_response = self.api_service.ws_valida_base_confiable(
                official)

            # Primero verifico que la API haya respondido bien
            if service_response['Erroresnegocio']:
                self.result['error'] = True
                self.result['message'] = service_response['Erroresnegocio']

            # Si encontró a la persona, checkea reliable_base
            if 'La Persona Existe' in service_response['Mensaje']:
                if official.reject_reason:
                    if 'Persona No Encontrada' in official.reject_reason:
                        official.reject_reason = None
                official.reliable_base = True
                self.result['ok'] = True
            elif 'Persona No Encontrada' in service_response['Mensaje']:
                self.result['pass'] = True
                self.result['message'].append(service_response['Mensaje'])
            else:
                self.result['error'] = True
                self.result['message'].append(service_response['Mensaje'])
            # DEBUG
            self.result['debug'] = service_response['debug']
        else:
            # Volver a verificar esta parte
            if official.reject_reason:
                if 'Persona No Encontrada' in official.reject_reason:
                    official.reject_reason = None
            self.result['ok'] = True
            self.result['message'] = 'El funcionario ya se encontró'
            # DEBUG
            self.result['debug'] = 'No se ejecuto la API: %(reason)s - %(msg)s' % ({
                'reason': '"{}" = {}'.format(
                    self._fields['reliable_base'].string, official.reliable_base
                ),
                'msg': self.result['message']
            })

        return self.result

    def ws_cliente_posee_cuenta(self, official):
        """
        # API: Cliente posee cuenta
        - Valído que el/los funcionarios posean cuenta
        """
        self.init_service()

        if not (official.account_number and official.account_name and official.branch_id):
            service_response = self.api_service.ws_cliente_posee_cuenta(
                official)

            # Primero verifico que la API haya respondido bien
            if service_response['Erroresnegocio']:
                self.result['error'] = True
                self.result['message'] = service_response['Erroresnegocio']

            # Verifico que la API me de la Cuenta y Sucursal
            if service_response['Cuenta'] and service_response['Sucursal']:
                if not official.account_number:
                    official.account_number = service_response['Cuenta']

                if not official.account_name:
                    official.account_name = service_response['Ttnom']

                if not official.branch_id and service_response['Sucursal']:
                    _branch = official.branch_id.search(
                        [('code', 'in', [service_response['Sucursal']])])
                    # Si NO encuentro el ID en la tabla, lo creo y le asigno un nombre
                    if not _branch:
                        _branch = official.branch_id.create({
                            'name': 'sucursal_{}'.format(service_response['Sucursal']),
                            'code': service_response['Sucursal']
                        })
                    official.branch_id = _branch
                # NO se usa: service_response['Cttfir']
                # NO se usa: service_response['Observacion']
                self.result['ok'] = True
            # DEBUG
            self.result['debug'] = service_response['debug']
        else:
            self.result['pass'] = True
            self.result['message'] = 'El funcionario ya posee cuenta'
            # DEBUG
            self.result['debug'] = 'No se ejecuto la API: %(reason)s - %(msg)s' % ({
                'reason': '"{}" = {} and "{}" = {} and "{}" = {}'.format(
                    self._fields['account_number'].string, official.account_number,
                    self._fields['account_name'].string, official.account_name,
                    self._fields['branch_id'].string, '({}) {}'.format(
                        official.branch_id.code, official.branch_id.name)
                ),
                'msg': self.result['message']
            })

        return self.result

    def ws_alta_cuenta(self, official):
        """
        # API: Alta de cuenta
        - Creación de cuentas de los funcionarios
        """
        self.init_service()

        service_response = self.api_service.ws_alta_cuenta(official)

        # Primero verifico que la API haya respondido bien
        if service_response['Erroresnegocio']:
            self.result['error'] = True
            self.result['message'] = service_response['Erroresnegocio']
        if 'Cuenta existente bajo el mismo contrato' in service_response['Mensaje']:
            self.result['pass'] = True
        elif service_response['CtNro'] == "0" or not len(service_response['CtNro']):
            self.result['error'] = True
            self.result['message'] = service_response['Mensaje']
        else:
            official.sudo().write({
                'account_number': service_response['CtNro'],
                'account_name': service_response['CtNom'],
                'account_registration': datetime.now()
            })
            self.result['ok'] = True
        # DEBUG
        self.result['debug'] = service_response['debug']

        return self.result

    def ws_alta_ca(self, official):
        """
        # API: Alta de Caja de Ahorro
        - Creación de las Cajas de Ahorro de los funcionarios
        """
        self.init_service()

        service_response = self.api_service.ws_alta_ca(official)

        # Primero verifico que la API haya respondido bien
        if service_response['Erroresnegocio']:
            self.result['error'] = True
            self.result['message'] = service_response['Erroresnegocio']

        # Verifico la respuesta
        if 'Se Generó la Caja de Ahorro' in service_response['Mensaje']:
            self.result['ok'] = True
        elif service_response['Mensaje'] in ['Cuenta existente bajo el mismo contrato',
                                             'Verificar el Limite Operativo de la Cuenta',
                                             'La cuenta ya cuenta con una caja de ahorro en la sucursal',
                                             'El Número de Subcuenta ya existe para el Producto.']:
            self.result['pass'] = True
            self.result['message'] = service_response['Mensaje']
        else:
            self.result['error'] = True
            self.result['message'] = service_response['Mensaje']

        # DEBUG
        self.result['debug'] = service_response['debug']

        return self.result

    def ws_estado_ca(self, official):
        """
        # API: Estado de la Caja de Ahorro
        - Valído el estado de las cuentas de los funcionarios
        """
        self.init_service()

        if official.account_number:
            service_response = self.api_service.ws_estado_ca(official)

            # Primero verifico que la API haya respondido bien
            if service_response['Erroresnegocio']:
                self.result['error'] = True
                self.result['message'] = service_response['Erroresnegocio']

            # Encuentro el estado dentro del dict _ACCOUNT_STATUS
            official_account_status = '999'  # Estado sin información
            for status in official._ACCOUNT_STATUS:
                if service_response['Scstat'] in status[0]:
                    official_account_status = status[0]
                    break
            official.sudo().write({
                'account_status': official_account_status,
                # 'account_module': service_response['Scmod']  El modulo se obtiene por la empresa del funcionario
            })
            # NO se usa service_response['Sccta']
            # NO se usa service_response['Scmda']
            # NO se usa service_response['Scsuc']

            # Verifico la respuesta
            if service_response['Scstat']:
                self.result['ok'] = True
            else:
                self.result['error'] = True
                self.result['message'] = 'No se obtuvo ningún estado'

            # DEBUG
            self.result['debug'] = service_response['debug']
        else:
            self.result['error'] = True
            self.result['message'] = 'El funcionario no posee cuenta'
            # DEBUG
            self.result['debug'] = 'No se ejecuto la API: %(reason)s - %(msg)s' % ({
                'reason': '"{}" = {}'.format(
                    self._fields['account_number'].string, official.account_number
                ),
                'msg': self.result['message']
            })

        return self.result

    def ws_alta_td(self, official):
        """
        # API: Alta de Tarjeta de Debito
        - Creación de las Tarjetas de Debito para los funcionarios
        """
        self.init_service()

        service_response = self.api_service.ws_alta_td(official)

        # Primero verifico que la API haya respondido bien
        if service_response['Erroresnegocio']:
            self.result['error'] = True
            self.result['message'] = service_response['Erroresnegocio']

        # Verifico la respuesta
        if 'Pendiente a Procesar por BANCARD' in service_response['Mensaje']:
            self.result['ok'] = True
        else:
            self.result['error'] = True
            self.result['message'] = service_response['Mensaje']

        # DEBUG
        self.result['debug'] = service_response['debug']
        return self.result

    def ws_estado_td(self, official):
        """
        # API: Estado de Tarjeta de Debito
        - Compruebo el estado de las Tarjetas de Debito para los funcionarios
        """
        self.init_service()

        service_response = self.api_service.ws_estado_td(official)

        # Primero verifico que la API haya respondido bien
        if service_response['Erroresnegocio']:
            self.result['error'] = True
            self.result['message'] = service_response['Erroresnegocio']

        if service_response['CUENTA']:
            self.result['ok'] = True
            self.result['data'] = {
                "CUENTA": service_response["CUENTA"],
                "MODULO": service_response["MODULO"],
                "MONEDA": service_response["MONEDA"],
                "SUCURSAL": service_response["SUCURSAL"],
                "ESTADO": service_response["ESTADO"],
                "PIN": service_response["PIN"]
            }
        else:
            self.result['error'] = True
            self.result['message'] = 'Sin datos para la consulta'

        # DEBUG
        self.result['debug'] = service_response['debug']

        return self.result

    def ws_control_cliente_payroll(self, official):
        """
        # API: Control Cliente Payroll
        - Compruebo el si los funcionarios tienen cobros en los ultimos 35 dias
        """
        self.init_service()

        service_response = self.api_service.ws_control_cliente_payroll(
            official)

        # Primero verifico que la API haya respondido bien
        if service_response['Erroresnegocio']:
            self.result['error'] = True
            self.result['message'] = service_response['Erroresnegocio']

        self.result['ok'] = True
        self.result['data'] = {
            "FcUltCobro": service_response['FcUltCobro'],
            "Ctfalt": service_response['Ctfalt'],
            "ENTFCBAJA": service_response['ENTFCBAJA'],
            "GxExiste": service_response['GxExiste']
        }

        # DEBUG
        self.result['debug'] = service_response['debug']

        return self.result

    def ws_consulta_cuenta_servicio(self, company_account):
        """
        # API: Control Cliente Payroll
        - Compruebo el si los funcionarios tienen cobros en los ultimos 35 dias
        """
        self.init_service()

        service_response = self.api_service.ws_consulta_cuenta_servicio(
            company_account)

        # Primero verifico que la API haya respondido bien
        if service_response['Erroresnegocio']:
            self.result['error'] = True
            self.result['message'] = service_response['Erroresnegocio']
        else:
            self.result['message'] = service_response['Mensaje']

        self.result['ok'] = (service_response['Mensaje'] == 'TRUE')
        self.result['data'] = {
            'NroContrato': service_response['NroContrato'],
            'DesContrato': service_response['DesContrato'],
            'Datos': service_response['Datos']
        }

        # DEBUG
        self.result['debug'] = service_response['debug']

        return self.result
