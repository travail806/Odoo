import calendar

from odoo import models, fields, api
from odoo.exceptions import ValidationError

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

import tempfile
import os
import base64

import logging

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    x_num_marche = fields.Char(string="Numéro de marché")
    x_num_order = fields.Char(string="Numéro d'engagement")

    billing_start_date = fields.Date(
        string="Debut de periode de facturation"
    )

    billing_end_date = fields.Date(
        string="Fin de periode de facturation"
    )

    @api.onchange('billing_start_date')
    def _onchange_billing_start_date(self):
        if self.billing_start_date:
            last_day = calendar.monthrange(self.billing_start_date.year,self.billing_start_date.month)[1]
            self.billing_end_date=self.billing_start_date.replace(day=last_day)

    @api.constrains('billing_start_date', 'billing_end_date')
    def _check_billing_dates(self):
        for move in self:
            if move.billing_start_date and move.billing_end_date:
                if move.billing_end_date < move.billing_start_date:
                    raise ValidationError(
                        "La date de fin de facturation doit etre posterieure a la date de debut."
                    )

    @api.onchange('billing_end_date')
    def _onchange_billing_dates_recompute_quantities(self):
        #_logger.info ("Recompute quantities ")
        for move in self:
            if not move.billing_start_date or not move.billing_end_date:
                continue

            for line in move.invoice_line_ids :
                if line.product_id and line.product_id.is_product_recurrent:
                    line.quantity = line._get_product_quantity( move.billing_start_date, move.billing_end_date )
    
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
