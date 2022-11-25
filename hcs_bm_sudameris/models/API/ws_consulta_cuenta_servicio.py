import requests
import json
import logging

logger = logging.getLogger(__name__)


class ApiWsConsultaCuentaServicio:
    """
    # Servicio: Consulta Cliente Payroll (últimos 35 días si cobro)
    Metodo: POST
    URL: http://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPAYROOL?ConsultaCuentaServicio
    """

    def __init__(self, base_url, authenticate):
        self.service = "ConsultaCuentaServicio"
        self.request_url = base_url + self.service
        self.authenticate = authenticate

    def ws_consulta_cuenta_servicio(self, cuenta, *args, **kwargs):
        """
        # Parametros
        - Btinreq:		Credenciales				Object
        - Cuenta:		Cuenta						N(9)

        # Response
        - Mensaje:		Código de retorno			C(100)
        - NroContrato:	Número de contrato (código) D(AAAA/MM/DD)
        - DesContrato:	Nombre de la empresa		D(AAAA/MM/DD)
        - Datos:
            - sBTCuenta_Lista:
                - Sucursal:	    Sucursal de la empresa		C(1)
                - Moneda:		Moneda de la empresa		C(1)
                - Cuenta:	    Cuenta de la empresa		C(1)
                - Modulo:		Modulo de la empresa        C(1)

        # Observación
        - Mensaje:      Si responde TRUE, devuelve los datos de la empresa
        """

        request_body = json.dumps({
            "Btinreq": self.authenticate['Btinreq'],
            "Cuenta": cuenta,
        })
        response = {
            "Mensaje": "",
            "NroContrato": "",
            "DesContrato": "",
            "Canales": "",
            "Datos": {},
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
                if 'NroContrato' in request:
                    response["NroContrato"] = request["NroContrato"]
                if 'DesContrato' in request:
                    response["DesContrato"] = request["DesContrato"]
                if 'Canales' in request:
                    response["Canales"] = request["Canales"]
                response["Mensaje"] = request["Mensaje"]
                response["Datos"] = request["Datos"]

        except Exception as e:
            exp_message = str(e)
            if 'HTTPConnectionPool' in exp_message:  # HTTPConnectionPool == Conection Timeout
                exp_message = '(HTTPConnectionPool): No se puede conectar al banco'
            logger.error([self.service, 'Exception',
                         exp_message], exc_info=True)
            response['debug'] = exp_message
            response["Erroresnegocio"] = exp_message

        return response
