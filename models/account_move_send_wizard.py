from odoo import models, api
import json


class AccountMoveSendWizard(models.TransientModel):
    _inherit = "account.move.send.wizard"

    @api.depends(
        'template_id',
        'invoice_edi_format',
        'extra_edis',
        'pdf_report_id'
    )
    def _compute_mail_attachments_widget(self):
        super()._compute_mail_attachments_widget()
        
        attachments = self.mail_attachments_widget or []    
   
        move = self.move_id
        if move:
            # Génération du PDF complémentaire
            training_attachment = move._generate_training_pdf_attachment()

            # Éviter les doublons
            existing_ids = {
                att.get("id")
                for att in attachments or []
            }

            if training_attachment.id not in existing_ids:
            
                new_attachment = {
                    'id': training_attachment.id,
                    'name': training_attachment.name,
                    'mimetype': training_attachment.mimetype,
                    'filename': training_attachment.name,
                    'placeholder': True,
                    'protect_from_deletion': False,
                }
                attachments.append(new_attachment)


                self.write({'mail_attachments_widget': attachments})
                self.write({'display_attachments_widget': True})    


