import logging
import requests
import json

logger = logging.getLogger(__name__)


class ApiWsAltaCuenta:
    """
        # Alta de Cuentas Payroll/Proveedores
        Metodo: POST
        URL: https://10.100.14.2:9280/bantotal/servlet/com.dlya.bantotal.odwsbt_BSPayroll?WSAltaCuenta
    """

    def __init__(self, base_url, authenticate):
        self.service = "WSAltaCuenta"
        self.request_url = base_url + self.service
        self.authenticate = authenticate

    def ws_alta_cuenta(self, official):
        """
        # Parametros
        Btinreq:        Credenciales                            |   Object
        CodEmpresa:     Codigo de la Empresa                    |   N(9)
        TpGrup:         Tipo de Grupo (90 Payroll, 94 Proveed)  |   N(3)
        Ejecutivo:      Ejecutivo                               |   N(3)
        TPContrato:     Tipo Contrato                           |   C(1)
        Pais:           País(*)                                 |   N(3)
        Tdoc:           Tipo de Documento(*)                    |   N(2)
        Ndoc:           Numero de Documento                     |   C(12)
        Nomb1:          Primer Nombre                           |   C(30)
        Nomb2:          Segundo Nombre                          |   C(30)
        Apell1:         Primer Apellido                         |   C(30)
        Apell2:         Segundo Apellido                        |   C(30)
        Pnac:           Pais de Nacimiento                      |   N(3)
        FecNac:         Fecha de Nacimiento                     |   D(AAAA/MM/DD)
        Sexo:           Sexo(M o F)                             |   C(1)
        Ecivil:         Estado Civil(*)                         |   C(1)
        venciDoc:       Vencimiento del Documento de Identidad  |   D(AAAA/MM/DD)
        Salario:        Salario                                 |   N(18.2)
        Fingreso:       Fecha de ingreso a la Empresa           |   D(AAAA/MM/DD)
        CodDirec:       Codigo dirección(Enviar siempre “1”)    |   N(3)
        DomicilioR:     Domicilio Real                          |   C(50)
        NroCasa:        Numero de Casa                          |   N(4)
        Ciudad:         Ciudad(*)                               |   N(5)
        Departamento:   Departamento(*)                         |   N(4)
        Barrio:         Barrio(*)                               |   N(9)
        CalleT:         Calle Transversal                       |   C(35)
        Referencia:     Referencia                              |   C(50)
        Dotelp:         Teléfono Particular                     |   C(20)
        Dotell:         Teléfono Laboral                        |   C(20)
        SubSegm:        SubSegmentacion(S o N)                  |   C(1)
        # RESPONSE
        CTNRO:          Cuenta                      |   N(9)
        CTNOM:          Descripción de la cuenta    |   C(30)
        CodRetorno:     Código de Retorno           |   N(3)
        Mensaje:        Nombre de Persona           |   C(100) # generar nueva tarjeta de débito
        """
        request_body = json.dumps({
            "Btinreq": self.authenticate['Btinreq'],
            "CodEmpresa": official.company_id.company_code,
            "Tgcod": official.group_type,
            "CodEjct": official.executive,
            "TContrato": official.contract_type,
            "CodSuc": official.branch_id.code,
            "PePais": official.country.code_number,
            "PeTdoc": official.identification_type,
            "PeNdoc": official.identification_id,
            "Nomb1": official.name_first,
            "Nomb2": official.name_second or '',
            "Apell1": official.surname_first,
            "Apell2": official.surname_second or '',
            "PfPnac": official.country_of_birth.code_number,
            "PfFnac": official.birthday.strftime("%Y/%m/%d"),
            "Sexo": official.gender,
            "PfEciv": official.marital,
            "IngSalario": official.gross_salary,
            "PfxEmcFch": official.admission_date.strftime("%Y/%m/%d"),
            "DomReal": official.real_address,
            "NroCasa": official.house_no,
            "DoDepCodP": official.city.code,
            "Barrio": official.neighborhood.code,
            "CalleT": official.street_transversal or '.',
            "Referencia": official.reference or '.',
            "TelCel": official.mobile_phone,
            "TelLab": official.work_phone or '.',
            "SubSegm": official.sub_segmentation
        })
        response = {
            "CodEjct": "",
            "CtNro": "",
            "CtNom": "",
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
                if 'CodEjct' in request:
                    response["CodEjct"] = request["CodEjct"]
                if 'CtNro' in request:
                    response["CtNro"] = request["CtNro"]
                if 'CtNom' in request:
                    response["CtNom"] = request["CtNom"]
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
