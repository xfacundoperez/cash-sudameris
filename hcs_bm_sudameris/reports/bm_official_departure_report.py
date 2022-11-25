""" from odoo import models


class BMOfficialDepartureReport(models.AbstractModel):
    _name = 'report.hcs_bm_sudameris.bm_official_departure_xlsx_template'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        sheet = workbook.add_worksheet('Desvinculados')
        # Formato Rojo con letras blancas
        header_format = workbook.add_format({
            'font_size': 10,
            'bold': True,
            'bg_color': "#ff0000",
            'font_color': '#ffffff'})
        _line = 0
        # Fila 1
        _header_text = ['SucEmpresa', 'Empresa', 'CodSuc', 'Sucursal', 'Cuenta',
                        'Cliente', 'C.I.N°', 'Motivo', 'Incorporación',
                        'Desvinculación', 'Liquidación', 'Aguinaldo']
        for idx, val in enumerate(_header_text):
            sheet.set_column(_line, idx, 15)
            sheet.write(_line, idx, val, header_format)

        # Fila 2 a N
        _line = 1
        # Por cada desvinculado, agrego más filas
        line_format = workbook.add_format({
            'font_size': 14,
            'align': 'vcenter',
            'bold': True
        })
        for official in lines:
            company_branch = self.env['bm.branch'].search(
                [('code', '=', official.company_id.branch_id.code)])
            for idx, val in enumerate(_header_text):
                if 'SucEmpresa' == val:
                    sheet.write(_line, idx, '{} {}'.format(
                        company_branch.code, company_branch.name) or 'S/D', line_format)
                if 'Empresa' == val:
                    sheet.write(_line, idx, '{} {}'.format(
                        official.company_id.company_code, official.company_id.name), line_format)
                if 'CodSuc' == val:
                    sheet.write(_line, idx, official.branch_id.code,
                                line_format)
                if 'Sucursal' == val:
                    sheet.write(_line, idx, official.branch_id.name or 'S/D', line_format)
                if 'Cuenta' == val:
                    sheet.write(_line, idx, official.account_number,
                                line_format)
                if 'Cliente' == val:
                    sheet.write(_line, idx, official.name,
                                line_format)
                if 'C.I.N°' == val:
                    sheet.write(_line, idx, official.identification_id,
                                line_format)
                if 'Motivo' == val:
                    sheet.write(_line, idx, dict(official.departured._fields['departure_reason'].selection).get(official.departured.departure_reason),
                                line_format)
                if 'Incorporación' == val:
                    sheet.write(_line, idx, official.admission_date.strftime("%d/%m/%Y"),
                                line_format)
                if 'Desvinculación' == val:
                    sheet.write(_line, idx, official.departured.departure_start.strftime("%d/%m/%Y") or '',
                                line_format)
                # Monto total Liquidación | Se puede colocar de 2 maneras. *Traer en blanco y que la empresa sea la que complete manualmente *al momento de seleccionar la desvinculacion en la herramienta que le solicite dicho dato
                if 'Liquidación' == val:
                    sheet.write(_line, idx, '',
                                line_format)
                # Monto del Aguinaldo correspondiente, protegido en base al Decreto Nro 5651/2010 | "Eliminar" dice el banco
                if 'Aguinaldo' == val:
                    sheet.write(_line, idx, '',
                                line_format)
            _line = _line + 1
 """
