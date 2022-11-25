import logging
import requests
import json

logger = logging.getLogger(__name__)


class ApiWsAltaCA:
    """
    # Alta de CAJA DE AHORRO
    Metodo: POST
    URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSAltaCA
    """

    def __init__(self, base_url, authenticate):
        self.service = "WSAltaCA"
        self.request_url = base_url + self.service
        self.authenticate = authenticate

    def ws_alta_ca(self, official, *args, **kwargs):
        """
        # Parametros
        Btinreq:	Credenciales		Object
        Cuenta:		Número de cuenta	N(9)
        Sucursal:	Número de sucursal	N(3)
        Modulo:		Módulo				N(3)
        Moneda:		Código de moneda	N(4)
        Estado:		Estado de alta(*)	N(2)
        # RESPONSE
        CodRetorno:	Código de Retorno	N(3)
        Mensaje:	Nombre de Persona	C(100)
        """
        request_body = json.dumps({
            "Btinreq": self.authenticate['Btinreq'],
            "Pgcod": 1,
            "CtNro": official.account_number,
            "Pgmoca": official.account_module,
            "Suc": official.branch_id.code,
            "PgMNac": official.currency_type,
            "Papel": 0,
            "Totope": 0,
            "Scsbop": 0
        })
        response = {
            "PCvNom": "",
            "CodRetorno": "",
            "Mensaje": "",
            "Erroresnegocio": "",
            "debug": ""
        }
        try:
            request = requests.post(self.request_url, data=request_body, headers={
                'Content-Type': 'application/json'}, verify=False, timeout=3)
            request = request.text
            response['debug'] = request
            logger.info([self.service, request])
            request = json.loads(request)

            for BTErrorNegocio in request['Erroresnegocio']['BTErrorNegocio']:
                response["Erroresnegocio"] = BTErrorNegocio['Descripcion']

            if not response['Erroresnegocio']:
                if 'PCvNom' in request:
                    response["PCvNom"] = request["PCvNom"]
                response["CodRetorno"] = request["CodRetorno"]
                response["Mensaje"] = request["Mensaje"]

        except Exception as e:
            exp_message = str(e)
            if 'HTTPConnectionPool' in exp_message:  # HTTPConnectionPool == Conection Timeout
                exp_message = '(HTTPConnectionPool): No se puede conectar al banco'
            logger.error([self.service, 'Exception',
                         exp_message], exc_info=True)
            response['debug'] = exp_message
            response["Erroresnegocio"] = exp_message

        return response
