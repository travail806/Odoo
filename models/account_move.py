from odoo import models, fields
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import os
import base64


class AccountMove(models.Model):
    _inherit = 'account.move'

    billing_start_date = fields.Date(
        string="Début de période de facturation"
    )

    billing_end_date = fields.Date(
        string="Fin de période de facturation"
    )

    def action_generate_training_pdf(self):
        self.ensure_one()

        # Création fichier temporaire
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

            events = line.get_events_between_dates()

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

            for event in events:
                duration = (event.stop - event.start).total_seconds() / 3600

                content.append(Paragraph(
                    f"- {event.name} | "
                    f"{event.start.strftime('%d/%m/%Y')} "
                    f"{event.start.strftime('%H:%M')} → "
                    f"{event.stop.strftime('%H:%M')} "
                    f"({duration:.2f} h)",
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

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{attachment.id}?download=true",
            "target": "self",
        }
