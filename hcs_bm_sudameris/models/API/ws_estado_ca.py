import requests
import json
import logging

logger = logging.getLogger(__name__)


class ApiWsEstadoCA:
    """
    Servicio: Estado de la Caja de Ahorro
    Metodo: POST
    URL: http://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPAYROOL?WSEstadoCA
    """

    def __init__(self, base_url, authenticate):
        self.service = "WSEstadoCA"
        self.request_url = base_url + self.service
        self.authenticate = authenticate

    def ws_estado_ca(self, official, *args, **kwargs):
        """
        # Parametros
        - Btinreq:		Credenciales		Object
        - Cuenta:		Número de cuenta	N(9)
        - Sucursal:		Número de sucursal	N(3)
        - Modulo:		Módulo  			N(3)
        - Moneda:		Código de moneda	N(4)

        # Response
        - Cuenta:		Número de cuenta	N(9)
        - Sucursal:		Número de sucursal	N(3)
        - Modulo:		Módulo(?)			N(3)
        - Moneda:		Código de moneda	N(4)
        - Estado:		Estado de la Cuenta	N(2)
        - CodRetorno:	Código de Retorno	N(2)
        - Observacion:	Nombre de Persona	C(100)

        # Observación
        - Sucursal		Si no se envía, se busca la Caja de Ahorro por Modulo y moneda
        - Observacion	Puede existir varias CA para una cuenta en sucursales distintas.
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
                        }
                    ]
                }
            }
        })
        response = {
            "Sccta": "",
            "Scmod": "",
            "Scmda": "",
            "Scstat": "",
            "Scsuc": "",
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

            for rec in request['Result']['Consultas']['RepCons.Consulta']:
                for column in rec['Columnas']['RepCols.Columna']:
                    if column['Descripcion'] == 'Sccta':
                        response["Sccta"] = column['Filas']['RepFilas.Fila'][0]['Valor'] if len(
                            column['Filas']['RepFilas.Fila']) else ""

                    if column['Descripcion'] == 'Scmod':
                        response["Scmod"] = column['Filas']['RepFilas.Fila'][0]['Valor'] if len(
                            column['Filas']['RepFilas.Fila']) else ""

                    if column['Descripcion'] == 'Scmda':
                        response["Scmda"] = column['Filas']['RepFilas.Fila'][0]['Valor'] if len(
                            column['Filas']['RepFilas.Fila']) else ""

                    if column['Descripcion'] == 'Scstat':
                        response["Scstat"] = column['Filas']['RepFilas.Fila'][0]['Valor'] if len(
                            column['Filas']['RepFilas.Fila']) else ""

                    if column['Descripcion'] == 'Scsuc':
                        response["Scsuc"] = column['Filas']['RepFilas.Fila'][0]['Valor'] if len(
                            column['Filas']['RepFilas.Fila']) else ""

        except Exception as e:
            exp_message = str(e)
            if 'HTTPConnectionPool' in exp_message:  # HTTPConnectionPool == Conection Timeout
                exp_message = '(HTTPConnectionPool): No se puede conectar al banco'
            logger.error([self.service, 'Exception',
                         exp_message], exc_info=True)
            response['debug'] = exp_message
            response["Erroresnegocio"] = exp_message

        return response
