import logging
import requests
import json

logger = logging.getLogger(__name__)


class ApiWsClientePoseeCuenta:
    """
    Servicio: Chequera Pendiente de Retiro
    Metodo: POST
    URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSClientePoseeCuenta
    """

    def __init__(self, base_url, authenticate):
        self.service = "WSClientePoseeCuenta"
        self.request_url = base_url + self.service
        self.authenticate = authenticate

    def ws_cliente_posee_cuenta(self, official, *args, **kwargs):
        """
        # Parametros
        - btinreq:		Credenciales		Object
        - Pais:			Pais				N(3)
        - Tdoc:			Tipo de Documento	N(2)
        - Ndoc:			Numero de Documento	C(12)

        # Response
        - Cuenta:		Cuenta				N(9)
        - Sucursal:		Sucursal			N(2)
        - Estado:		Estado de la Cuenta	C(1)
        - CodRetorno	Codigo de Retorno	N(3)
        - Mensaje		Nombre de Persona	C(100)

        # Observación:
        - Cuenta:		Devuelve cuenta individual
        """
        request_body = json.dumps({
            "Btinreq": self.authenticate['Btinreq'],
            "Parametros": {
                "Parametro": {
                    "sBTRepParametros.It": [{
                        "Tipo": "Entero",
                        "Nombre": "PAIS",
                        "Codigo": 1,
                        "Valor": official.country.code_number
                    }, {
                        "Tipo": "Entero",
                        "Nombre": "TDOC",
                        "Codigo": 2,
                        "Valor": official.identification_type
                    }, {
                        "Tipo": "Texto",
                        "Nombre": "NDOC",
                        "Codigo": 3,
                        "Valor": official.identification_id
                    }]
                }
            }
        })
        response = {
            "Cuenta": "",
            "Sucursal": "",
            "Ttnom": "",
            "Cttfir": "",
            "Observacion": "",
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
                for rec in request['Result']['Consultas']['RepCons.Consulta']:
                    for column in rec['Columnas']['RepCols.Columna']:
                        if column['Descripcion'] == 'CTNRO':
                            response["Cuenta"] = column['Filas']['RepFilas.Fila'][0]['Valor'] if len(
                                column['Filas']['RepFilas.Fila']) else ""

                        if column['Descripcion'] == 'SUCURSAL':
                            response["Sucursal"] = column['Filas']['RepFilas.Fila'][0]['Valor'] if len(
                                column['Filas']['RepFilas.Fila']) else ""

                        if column['Descripcion'] == 'Ttnom':
                            response["Ttnom"] = column['Filas']['RepFilas.Fila'][0]['Valor'] if len(
                                column['Filas']['RepFilas.Fila']) else ""

                        if column['Descripcion'] == 'Cttfir':
                            response["Cttfir"] = column['Filas']['RepFilas.Fila'][0]['Valor'] if len(
                                column['Filas']['RepFilas.Fila']) else ""

                        if column['Descripcion'] == 'Observacion':
                            response["Observacion"] = column['Filas']['RepFilas.Fila'][0]['Valor'] if len(
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
