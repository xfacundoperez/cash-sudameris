# -*- coding: utf-8 -*-
{
    'name': "Sudameris: Bank Management TEST",
    'version': '1.0',

    'category': 'Human Resources/Employees',

    'summary': 'Sudameris: Centraliza la información de funcionarios por compañias asociadas',

    'description': """
        Sudameris: Centraliza la información de funcionarios por compañias asociadas

        Organizá la plantilla de funcionarios y salarios por compañía asociada al banco
    """,
    'author': "HC Sinergia",
    'website': "http://www.hcsinergia.com",
    # 'sequence': 99,
    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'contacts', 'report_xlsx', 'password_security'],
    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/bm_official_wizard_views.xml',
        'wizard/bm_official_salary_wizard_views.xml',
        'wizard/bm_official_departure_wizard_views.xml',
        'reports/bm_official_salary_report.xml',
        'reports/bm_official_departure_report.xml',
        'reports/bm_official_account_report.xml',
        'views/assets.xml',
        'views/webclient_templates.xml',
        'views/res_country.xml',
        'views/res_company.xml',
        'views/bm_branch.xml',
        'views/bm_official.xml',
        'views/bm_official_departure.xml',
        'views/bm_official_salary.xml',
        'views/bm_product.xml',
        'views/bm_job.xml',
        'views/bm_department.xml',
        'views/bm_views.xml',
        'views/res_users.xml',
        'data/bm_data_branch.xml',
        'data/bm_data_ir_cron.xml',
        'data/bm_data_mail_channel.xml',
        'data/bm_data_config.xml',
        'data/bm_data_product.xml',
        'data/bm_data_res_country.xml'
    ],
    'installable': True,
    'application': True
}
