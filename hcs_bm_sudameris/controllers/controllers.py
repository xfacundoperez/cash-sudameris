# -*- coding: utf-8 -*-
from odoo import http
from datetime import datetime
import tempfile
try:
    from BytesIO import BytesIO
except ImportError:
    from io import BytesIO
import zipfile
from odoo.addons.web.controllers.main import content_disposition

#import logging
#_logger = logging.getLogger(__name__)


class BM_OfficialSalary_Controller(http.Controller):
    @http.route('/web/binary_text/create_file_txt', type='http', auth="user")
    def index(self, req):
        # Si no se pasaron ids, no genera nada
        if not req.params.get('ids'):
            return False
        _now = datetime.now()
        _ids = [int(_id) for _id in req.params.get(
            'ids').split(',')]  # Convierto los str a int
        _fecha_pago = _now.strftime("%d/%m/%Y")
        # Referencia: AÑO MES DIA HORA MIN SEG CODEMPRESA
        _referencia = '{}{}'.format(_now.strftime(
            "%Y%m%d%H%M%S"), req.params.get('code'))
        # Concepto
        _concepto = 'Pago_de_Salario_via_Banco'

        # Get the selected official's salary movement
        officials_salary = http.request.env['bm.official.salary'].search([
                                                                         ('id', 'in', _ids)])
        # Creo el TXT
        # Tipo de dato: I: Entero, C: Caracter o Alfanumérico, D: Fecha, N: Numérico decimal con dos valores decimales
        # Composición del nombre: ENTIDAD_SERVICIO_FECHA+HORA.TXT
        txt_title = '{}_{}.txt'.format(_concepto, _referencia)
        file_content_detail = ''
        _amount_to_pay_sum = 0
        for official_salary in officials_salary:
            _amount_to_pay_sum += official_salary.amount_to_pay
            file_content_detail += "{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{};{}\n".format(
                # Identificador del detalle(C:1)
                'D',
                # Concepto(C:30)
                _concepto,
                # Primer Apellido(C:15)
                official_salary.official.surname_first,
                # Segundo Apellido(C:15)
                official_salary.official.surname_second or '',
                # Primer Nombre(C:15)
                official_salary.official.name_first,
                # Segundo Nombre(C:15)
                official_salary.official.name_second or '',
                # País(I:3)
                official_salary.official.country.code_number,
                # Tipo de Documento(I:2)
                official_salary.official.identification_type,
                # Número de Documento(C:15)
                official_salary.official.identification_id,
                # Moneda(I:4)
                official_salary.official.currency_type,
                # Importe(N:15.2)
                "%.2f" % official_salary.amount_to_pay,
                official_salary.payment_date.strftime(
                    "%d/%m/%Y") or '',    # Fecha de Pago(D:8)
                # Modalidad de Pago(I:3)
                official_salary.payment_mode or '',
                # Número de Cuenta(I:9)
                official_salary.official.account_number or '',
                # Sucursal Empleado(I:3)
                official_salary.official.branch_id.code,
                # Moneda Empleado(I:4)
                official_salary.official.currency_type,
                # Operación Empleado(I:9): En estos campos va siempre el numero 0
                '0',
                # Tipo de Operación Empleado(I:3): En estos campos va siempre el numero 0
                '0',
                # Suboperación Empleado(I:3): En estos campos va siempre el numero 0
                '0',
                # Referencia(C:18): Dicho campo debe ser exactamente igual que el campo REFERENCIA en la CABECERA
                _referencia,
                # Tipo de Contrato(I:3): Este campo se coloca siempre el numero 1
                '1',
                # Sueldo Bruto(N:15.2)
                "%.2f" % official_salary.official.gross_salary or '0.00',
                # Fecha Fin de Contrato(D:8)
                official_salary.official.contract_end_date or '//',
            )

        # Sueldo o Aguinaldo
        sac = req.params.get('sac')

        company_debit = http.request.env.user.company_id.bantotal_account
        company_currency = '6900'  # Guaranies
        if http.request.env.user.company_id.currency_id.name == 'USD':
            company_currency = '1'  # Guaranies

        file_content_header = '{};{};{};{};{};{};{};{};{};1;{};10;20;{};0;0;0\n'.format(
            'H',                            # Identificador de cabecera(C:1)
            '999',                          # Código de contrato(I:9)
            'mail@entidad.com',             # E-mail asociado al Servicio(C:50)
            company_currency,               # Moneda(I:4)
            "%.2f" % _amount_to_pay_sum,    # Importe(N:15.2)
            len(_ids),                      # Cantidad de Documentos(I:5)
            _fecha_pago,                    # Fecha de Pago(D:8)
            _referencia,                    # Referencia(C:18)
            sac,                            # Tipo de Cobro(I:3)
            '1',                            # Debito Crédito(I:1)
            company_debit,                  # Cuenta Débito(I:9)
            '10',                           # Sucursal Débito(I:3)
            '20',                           # Módulo Débito(I:3)
            company_currency,               # Moneda Débito(I:4)
            '0',                            # Operación Débito(I:9)
            '0',                            # Sub Operación Débito(I:3)
            '0'                             # Tipo Operación Débito(I:3)
        )

        # Creo el archivo TXT
        txt_content = str.encode(file_content_header + file_content_detail)

        # Create temporary file, write info and download
        txt_temp = tempfile.TemporaryFile()
        # Write data into your file respectively with your logic
        txt_temp.write(txt_content)
        txt_temp.seek(0)
        txt_file = txt_temp.read()
        txt_temp.close()

        # Creo el PDF
        report = req.env.ref('hcs_bm_sudameris.bm_official_salary_report')
        pdf_report = report.sudo().render_qweb_pdf(
            _ids, {'sac': sac, 'referencia': _referencia})[0]
        pdf_title = '{}_{}.pdf'.format(_concepto, _referencia)

        tmp_pdf = tempfile.TemporaryFile()
        tmp_pdf.write(pdf_report)
        tmp_pdf.seek(0)
        pdf = tmp_pdf.read()
        tmp_pdf.close()

        zip_filename = _now
        zip_filename = "%s.zip" % zip_filename
        bitIO = BytesIO()
        with zipfile.ZipFile(bitIO, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr(txt_title, txt_file)
            zf.writestr(pdf_title, pdf)
        return req.make_response(bitIO.getvalue(),
                                 headers=[('Content-Type', 'application/x-zip-compressed'),
                                          ('Content-Disposition', content_disposition(zip_filename))])

    @http.route(['/web/binary_pdf/<string:ids>'], type='http', auth="user", website=True)
    def download_pdf(self, req, ids):
        ids = [int(_id) for _id in ids.split(',')]  # Convierto los str a int
        # Filtro solo los IDS que posean fecha de registro
        ids = http.request.env['bm.official'].search(
            ['&', ('id', 'in', ids), ('account_registration', '!=', None)]).ids
        # Si no encunetra ninguno, exit
        if not ids:
            return None

        report = req.env.ref('hcs_bm_sudameris.bm_official_account_report')
        pdf = report.sudo().render_qweb_pdf(ids)[0]
        pdf_http_headers = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf)),
                            ('Content-Disposition', content_disposition('alta_de_cuentas.pdf'))]
        return req.make_response(pdf, headers=pdf_http_headers)
