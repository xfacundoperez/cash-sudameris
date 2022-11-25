import requests
import json
import logging

logger = logging.getLogger(__name__)


class ApiWsControlClientePayroll:
    """
    # Servicio: Consulta Cliente Payroll (últimos 35 días si cobro)
    Metodo: POST
    URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSControlClientePayroll
    """

    def __init__(self, base_url, authenticate):
        self.service = "WSControlClientePayroll"
        self.request_url = base_url + self.service
        self.authenticate = authenticate

    def ws_control_cliente_payroll(self, official, *args, **kwargs):
        """
        # Parametros
        - Btinreq:		Credenciales				Object
        - Cuenta:		Cuenta						N(9)
        - Ctccli:		Codigos de Clasificación	N(9)

        # Response
        - FcUltCobro:	Fecha de ultimo cobro		D(AAAA/MM/DD)
        - Ctfalt:		Fecha de alta				D(AAAA/MM/DD)
        - ENTFCBAJA:	Fecha de baja				D(AAAA/MM/DD)
        - GxExiste:		Clasificación si es Payroll	C(1)
        - CodRetorno:	Código de Retorno			N(3)
        - Mensaje:		Nombre de Persona			C(100)

        # Observación
        - Ctccli		Por código de empresa
        - GxExiste		S: es Payroll, N: no es Payroll, '': nunca fue PayRoll, A: pendiente a cobrar
        """
        request_body = json.dumps({
            "Btinreq": self.authenticate['Btinreq'],
            "CTNRO": official.account_number,
            "CtCCli": official.company_id.company_code
        })
        response = {
            "FcUltCobro": "0000-00-00",
            "Ctfalt": "",
            "ENTFCBAJA": "",
            "GxExiste": "",
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
                if 'FcUltCobro' in request:
                    response["FcUltCobro"] = request["FcUltCobro"]
                if 'Ctfalt' in request:
                    response["Ctfalt"] = request["Ctfalt"]
                if 'ENTFCBAJA' in request:
                    response["ENTFCBAJA"] = request["ENTFCBAJA"]
                if 'GxExiste' in request:
                    response["GxExiste"] = request["GxExiste"]
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
