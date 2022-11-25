import requests
import json
import logging

logger = logging.getLogger(__name__)


class ApiWsEstadoTD:
    """
    # Servicio: Estado de la Tarjeta de Debito
    Metodo: POST
    URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSEstadoTD
    """

    def __init__(self, base_url, authenticate):
        self.service = "WSEstadoTD"
        self.request_url = base_url + self.service
        self.authenticate = authenticate

    def ws_estado_td(self, official, *args, **kwargs):
        """
        # Parametros
        - Btinreq:		Credenciales		Object
        - Cuenta:		Número de cuenta	N(9)
        - Moneda:		Código de moneda	N(4)

        # Response
        - Estado		Estado de la Cuenta	N(2)
        - Observacion	Observacion			C(100)

        # Observación
        - Observacion	Observaciones, Descripcion del Estado
        """
        request_body = json.dumps({
            "Btinreq": self.authenticate['Btinreq'],
            "Parametros": {
                "Parametro": {
                    "sBTRepParametros.It": [
                        {
                            "Tipo": "Texto",
                            "Nombre": "CUENTA",
                            "Codigo": 5,
                            "Valor": official.account_number
                        },
                        {
                            "Tipo": "Entero",
                            "Nombre": "MODULO",
                            "Codigo": 6,
                            "Valor": official.account_module
                        },
                        {
                            "Tipo": "Entero",
                            "Nombre": "MONEDA",
                            "Codigo": 7,
                            "Valor": official.currency_type
                        },
                        {
                            "Tipo": "Entero",
                            "Nombre": "SUCURSAL",
                            "Codigo": 8,
                            "Valor": official.branch_id.code
                        }
                    ]
                }
            }
        })
        response = {
            "CUENTA": "",
            "MODULO": "",
            "MONEDA": "",
            "SUCURSAL": "",
            "ESTADO": "",
            "PIN": "",
            "Erroresnegocio": "",
            "debug": ""
        }
        try:
            request = requests.post(self.request_url, data=request_body, headers={
                'Content-Type': 'application/json'}, verify=False, timeout=3)
            request = request.text
            response['debug'] = request
            logger.info([self.service, response['debug']])
            request = json.loads(request)

            for BTErrorNegocio in request['Erroresnegocio']['BTErrorNegocio']:
                response['Erroresnegocio'] = BTErrorNegocio['Descripcion']

            if not response['Erroresnegocio']:
                for resp in response['Result']['Consultas']['RepCons.Consulta']:
                    for columna in resp['Columnas']['RepCols.Columna']:
                        if columna['Descripcion'] == 'CUENTA':
                            response["CUENTA"] = columna['Filas']['RepFilas.Fila'][0]['Valor'] if len(
                                columna['Filas']['RepFilas.Fila']) else ""

                        if columna['Descripcion'] == 'MODULO':
                            response["MODULO"] = columna['Filas']['RepFilas.Fila'][0]['Valor'] if len(
                                columna['Filas']['RepFilas.Fila']) else ""

                        if columna['Descripcion'] == 'MONEDA':
                            response["MONEDA"] = columna['Filas']['RepFilas.Fila'][0]['Valor'] if len(
                                columna['Filas']['RepFilas.Fila']) else ""

                        if columna['Descripcion'] == 'SUCURSAL':
                            response["SUCURSAL"] = columna['Filas']['RepFilas.Fila'][0]['Valor'] if len(
                                columna['Filas']['RepFilas.Fila']) else ""

                        if columna['Descripcion'] == 'ESTADO':
                            response["ESTADO"] = columna['Filas']['RepFilas.Fila'][0]['Valor'] if len(
                                columna['Filas']['RepFilas.Fila']) else ""

                        if columna['Descripcion'] == 'PIN':
                            response["PIN"] = columna['Filas']['RepFilas.Fila'][0]['Valor'] if len(
                                columna['Filas']['RepFilas.Fila']) else ""

        except Exception as e:
            exp_message = str(e)
            if 'HTTPConnectionPool' in exp_message:  # HTTPConnectionPool == Conection Timeout
                exp_message = '(HTTPConnectionPool): No se puede conectar al banco'
            logger.error([self.service, 'Exception',
                         exp_message], exc_info=True)
            response['debug'] = exp_message
            response["Erroresnegocio"] = exp_message

        return response
