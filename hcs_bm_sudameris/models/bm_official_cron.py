# -*- coding: utf-8 -*-
from odoo import models

import logging
logger = logging.getLogger(__name__)

class BM_OfficialCron(models.Model):
    _inherit = 'bm.official'

    def _notify_official_cam_reject(self):
        """
        # Notificacion de funcionarios rechazados CAM
        - Notifica a los usuarios con "perfil empresa" los rechazos realizados por el CAM
        """
        _subject = "Rechazo del funcionario"

        # Solo analizo si encontro mensajes
        messages = self.env['mail.message'].sudo().search([('subject', '=', _subject)])
        if messages:
            companies = {}
            for msg in  messages:
                off = self.search([('id', '=', msg.res_id)])
                # Solo si existe el funcionario y no se eliminó el registro
                if off:
                    if off.company_id.id not in companies:
                        companies[off.company_id.id] = {}
                        companies[off.company_id.id]['name'] = off.company_id.name
                        companies[off.company_id.id]['officials'] = {}
                        companies[off.company_id.id]['officials'][off.name] = {}
                        companies[off.company_id.id]['officials'][off.name]['cedule'] = off.identification_id
                        companies[off.company_id.id]['officials'][off.name]['reject_reasons'] = [msg.body]
                    else:
                        companies[off.company_id.id]['officials'][off.name]['reject_reasons'].append(msg.body)

                # Cambio el Subject como procesado
                msg.subject = "%(subject)s (_procesado_)" % ({
                    'subject': _subject
                })
        
            # Mensaje a mostrar
            for cid, company in companies.items():
                _body = "Se rechazo el alta los siguientes funcionarios:<br>"
                _subject_company = "%(subject)s (%(name)s)" % ({
                    'subject': _subject,
                    'name': company['name']
                })

                for of_name, of_data in company['officials'].items():
                    _body += "<br>%(name)s (%(cedule)s): " % ({
                        'name': of_name,
                        'cedule':  of_data['cedule'],
                    })
                    for reject_reason in of_data['reject_reasons']:
                        _body += "<br>%(reject)s" % ({
                            'reject': reject_reason
                        })

                # Notifico a los usuarios "Perfil empresa" de la empresa 
                # y a los usuarios del perfil banco
                logger.info([cid, _subject_company, _body])
                self.notify_to_company_users(cid, _subject_company, _body)

    def _notify_official_refer_cp(self):
        """
        # Notificacion de funcionarios a aprobar
        - Notifica a los usuarios de Centro Payroll que tiene altas de cuentas pendientes
        """
        _subject = "Funcionario a aprobar"

        messages = self.env['mail.message'].sudo().search([('subject', '=', _subject)])
        # Solo si encontro mensajes
        if messages:
            companies = {}
            for msg in  messages:
                off = self.search([('id', '=', msg.res_id)])
                # Solo si existe el funcionario y no se eliminó el registro
                if off:
                    if off.company_id.id not in companies:
                        companies[off.company_id.id] = {}
                        companies[off.company_id.id]['name'] = off.company_id.name
                        companies[off.company_id.id]['officials'] = [off.id]
                    else:
                        companies[off.company_id.id]['officials'].append(off.id)

                # Cambio el Subject como procesado
                msg.subject = "%(subject)s (procesado)" % ({
                    'subject': _subject
                })
            

            # Mensaje a mostrar
            _body = "Tiene nuevas solicitudes de alta de cuentas:"
            for cid, company in companies.items():
                _body += "<br>%(name)s: %(count)s cuenta(s) pendiente(s)" % ({
                    'name': company['name'],
                    'count':  len(company['officials'])
                })

            _message_subject = "%(subject)s (Notificacion a Centro Payroll)" % ({
                'subject': _subject
                })

            logger.info([cid, _message_subject, _body])
            # Referencia del Canal: Centro Payroll
            channel_name = 'bm_mail_channel_group_bm_bank_payroll'  
            # Envio la notificación
            self.notify_to_channel_users(channel_name, _message_subject, _body)

    def _notify_official_out_of_hours(self):
        """
        # Notificacion de cambios fuera de horario
        - Notifica a los usuarios de Centro Payroll que hubo cambios fuera de horario
        """
        _subject = "Cambios fuera de horario"

        messages = self.env['mail.message'].sudo().search([('subject', '=', _subject)])
        # Solo si encontro mensajes
        if messages:
            companies = {}
            for msg in  messages:
                off = self.search([('id', '=', msg.res_id)])
                # Solo si existe el funcionario y no se eliminó el registro
                if off:
                    if off.company_id.id not in companies:
                        companies[off.company_id.id] = {}
                        companies[off.company_id.id]['name'] = off.company_id.name
                        companies[off.company_id.id]['officials'] = {}
                        companies[off.company_id.id]['officials'][off.name] = {}
                        companies[off.company_id.id]['officials'][off.name]['cedule'] = off.identification_id

                # Cambio el Subject como procesado
                msg.subject = "%(subject)s (procesado)" % ({
                    'subject': _subject
                })

            # Mensaje a mostrar
            _body = "Se realizaron %(subject)s en los siguientes funcionarios:<br>" % ({
                'subject': _subject.lower()
            })
            for cid, company in companies.items():
                _body += "<br>%(name)s: " % ({
                    'name': company['name']
                    })

                for of_name, of_data in company['officials'].items():
                    _body += "<br> - %(name)s (%(cedule)s)" % ({
                        'name': of_name,
                        'cedule':  of_data['cedule'],
                    })

            _message_subject = "%(subject)s (Notificacion a Centro Payroll)" % ({
                'subject': _subject
                })

            logger.info([cid, _message_subject, _body])
            # Referencia del Canal: Centro Payroll
            channel_name = 'bm_mail_channel_group_bm_bank_payroll'  
            # Envio la notificación
            self.notify_to_channel_users(channel_name, _message_subject, _body)
