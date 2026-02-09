from odoo import models, fields, api
from odoo.exceptions import ValidationError

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

import tempfile
import os
import base64


class AccountMove(models.Model):
    _inherit = 'account.move'

    billing_start_date = fields.Date(
        string="Debut de periode de facturation"
    )

    billing_end_date = fields.Date(
        string="Fin de periode de facturation"
    )

    @api.constrains('billing_start_date', 'billing_end_date')
    def _check_billing_dates(self):
        for move in self:
            if move.billing_start_date and move.billing_end_date:
                if move.billing_end_date < move.billing_start_date:
                    raise ValidationError(
                        "La date de fin de facturation doit etre posterieure a la date de debut."
                    )


    
    def _generate_training_pdf_attachment(self):
        self.ensure_one()

        fd, path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)

        doc = SimpleDocTemplate(path)
        styles = getSampleStyleSheet()
        content = []

        content.append(Paragraph(
            f"<b>Relevé des formations facturées</b><br/>Facture : {self.name}",
            styles["Title"]
        ))

        for line in self.invoice_line_ids:
            if not line.product_id:
                continue

            product = self.env['product.product'].browse(line.product_id.id)
        
            events = line.get_events_between_dates(self.billing_start_date,self.billing_end_date)

            content.append(Paragraph(
                f"<br/><b>Formation :</b> {line.product_id.name}",
                styles["Heading2"]
            ))

            if not events:
                content.append(Paragraph(
                    "Aucun événement sur la période.",
                    styles["Normal"]
                ))
                continue
            #Filter only events related to the product
            for event in events:
                rec_prod_id = event['reccurent_product'].id
                #_logger.info ("ID de RECURRENT_PRODUCT %s" % (rec_prod_id))
                rec_prod= self.env['product.product'].browse(rec_prod_id);

                if rec_prod.id == product.id:

                    content.append(Paragraph(
                        f"- {event['name']} | "
                        f"{event['start'].strftime('%d/%m/%Y')} "
                        f"{event['start'].strftime('%H:%M')} → "
                        f"{event['stop'].strftime('%H:%M')} "
                        f"({event['duration']:.2f} h)",
                        styles["Normal"]
                    ))

        doc.build(content)

        with open(path, "rb") as f:
            pdf_data = base64.b64encode(f.read())

        os.remove(path)

        # attachment = self.env["ir.attachment"].create({
        #     "name": f"releve_formations_{self.name}.pdf",
        #     "type": "binary",
        #     "datas": pdf_data,
        #     "res_model": "account.move.send.wizard",
        #     "res_id": wizard_id,
        #     "mimetype": "application/pdf",
        # })

        attachment = self.env["ir.attachment"].create({
        "name": f"releve_formations_{self.name}.pdf",
        "type": "binary",
        "datas": pdf_data,
        "res_model": "account.move",
        "res_id": self.id,
        "mimetype": "application/pdf",
    })

        return attachment

    def action_generate_training_pdf(self):
        attachment = self._generate_training_pdf_attachment()

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }

    def action_invoice_sent(self):
        res = super().action_invoice_sent()

        self.ensure_one()

        attachment = self._generate_training_pdf_attachment()

        if res and "context" in res:
            attachments = res["context"].get("default_attachment_ids", [])
            attachments.append(attachment.id)

            res["context"]["default_attachment_ids"] = attachments

        return res
