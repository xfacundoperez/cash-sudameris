import logging
import requests
import json

logger = logging.getLogger(__name__)


class ApiWsAltaTD:
    """
    # Servicio: Alta de TD (MAESTRO-VISA)
    Metodo: POST
    URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSAltaTD
    """

    def __init__(self, base_url, authenticate):
        self.service = "WSAltaTD"
        self.request_url = base_url + self.service
        self.authenticate = authenticate

    def ws_alta_td(self, official, *args, **kwargs):
        """
        # Parametros
        Btinreq:	Credenciales			Object
        CodEmpresa:	Código Empresa			N(9)
        Ctnro:		Número de Cuenta		N(9)
        Pendoc:		Numero de Documento		C(12)
        Pepais:		País					N(3)
        PetDoc:		Tipo de Documento		N(2)
        CodSuc:		Sucursal				N(2)
        ScMod:		Modulo Cuentas Vistas	N(2)
        ScMda:		Moneda					N(4)
        Tiptar:		Tipo de Tarjeta			N(3)
        # RESPONSE
        CodRetorno:	Código de Retorno		N(3)
        Mensaje:	Nombre de Persona		C(100)
        """
        request_body = json.dumps({
            "Btinreq": self.authenticate['Btinreq'],
            "CodEmpresa": official.company_id.company_code,
            "Ctnro": official.account_number,
            "PeNdoc": official.identification_id,
            "PePais": official.country.code_number,
            "PeTdoc": official.identification_type,
            "CodSuc": official.branch_id.code,
            "ScMod": official.account_module,
            "ScMda": official.currency_type,
            "Tiptar": 3
        })
        response = {
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
            logger.info(['ws_alta_td', request])
            request = json.loads(request)

            for BTErrorNegocio in request['Erroresnegocio']['BTErrorNegocio']:
                response["Erroresnegocio"] = BTErrorNegocio['Descripcion']

            if not response['Erroresnegocio']:
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
