import logging
import requests
import json

logger = logging.getLogger(__name__)


class ApiWsValidaBaseConfiable:
    """
    # Servicio: Validación de documentos contra la base BCP/BASE CONFIABLE
    Metodo: POST
    URL: http://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPAYROOL?WSValidaBaseConfiable
    """

    def __init__(self, base_url, authenticate):
        self.service = "WSValidaBaseConfiable"
        self.request_url = base_url + self.service
        self.authenticate = authenticate

    def ws_valida_base_confiable(self, official):
        """
        # Parametros
        - btinreq:		Credenciales		Object
        - Pais:			País				N(3)
        - Tdoc:			Tipo de Documento	N(2)
        - Ndoc:			Número de Documento	C(12)
        - Nomb1:		Primer Nombre		C(25)
        - Nomb2:		Segundo Nombre		C(25)
        - Apell1:		Primer Apellido		C(30)
        - Apell2:		Segundo Apellido	C(30)
        - FecNac:		Fecha de Nac		D(AAAA/MM/DD)

        # Response
        - CodMensaje	Codigo de Retorno	N(2)
        - Mensaje		Nombre de Persona	C(100)

        # Observación: Contenido de "Mensaje"
        - No coincide Fecha de Nacimiento.
        - No coinciden Nombres.
        - No coinciden Apellidos.
        - Persona No Encontrada.
        """
        request_body = json.dumps({
            "Btinreq": self.authenticate['Btinreq'],
            "Pais": official.country.code_number,
            "Tdoc": official.identification_type,
            "Ndoc": official.identification_id,
            "Nomb1": official.name_first,
            "Nomb2": official.name_second or "",
            "Apell1": official.surname_first,
            "Apell2": official.surname_second or "",
            "FecNac": official.birthday.strftime("%Y/%m/%d") or ""
        })
        response = {
            "CodMensaje": "",
            "Mensaje": "",
            "Erroresnegocio": ""
        }
        try:
            request = requests.post(self.request_url, data=request_body, headers={
                'Content-Type': 'application/json'}, verify=False, timeout=3)
            request = request.text
            logger.info([self.service, request])
            request = json.loads(request)

            for BTErrorNegocio in request['Erroresnegocio']['BTErrorNegocio']:
                response["Erroresnegocio"] = BTErrorNegocio['Descripcion']

            if not response['Erroresnegocio']:
                response["CodMensaje"] = request["CodMensaje"]
                response["Mensaje"] = request["Mensaje"]

        except Exception as e:
            exp_message = str(e)
            if 'HTTPConnectionPool' in exp_message:  # HTTPConnectionPool == Conection Timeout
                exp_message = '(HTTPConnectionPool): No se puede conectar al banco'
            logger.error([self.service, 'Exception',
                         exp_message], exc_info=True)
            response["Erroresnegocio"] = exp_message

        return response
