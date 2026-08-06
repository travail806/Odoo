import calendar

from odoo import models, fields, api
from odoo.exceptions import ValidationError

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Image,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from reportlab.lib.units import cm

from reportlab.lib.styles import getSampleStyleSheet

import tempfile
import os
import io
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

        company = self.company_id

        # Logo
        logo = ""
        if company.logo:
            logo_stream = io.BytesIO(base64.b64decode(company.logo))
            logo = Image(logo_stream, width=4*cm, height=4*cm)

        # Adresse
        address = f"""
        <b>{company.name}</b><br/>
        {company.street or ''}<br/>
        {company.street2 or ''}<br/>
        {company.zip or ''} {company.city or ''}<br/>
        {company.country_id.name or ''}<br/>
        Tél : {company.phone or ''}<br/>
        Email : {company.email or ''}
        """

        address_paragraph = Paragraph(address, styles["Normal"])

        header = Table(
            [[logo, address_paragraph]],
            colWidths=[5 * cm, 12 * cm]
        )

        header.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (0, 0), "LEFT"),
            ("ALIGN", (1, 0), (1, 0), "RIGHT"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ]))

        content.append(header)

        content.append(Paragraph(
            f"Détail - Facture : {self.name} <br/>",
            styles["Title"]
        ))

        for line in self.invoice_line_ids:
            if not line.product_id:
                continue

            product = self.env['product.product'].browse(line.product_id.id)
        
            events = line.get_events_between_dates(self.billing_start_date,self.billing_end_date)

            content.append(Paragraph(
                #f"<br/><b>Formation :</b> {line.product_id.name}",
                f"<br/>",
                styles["Heading2"]
            ))

       
            table_data = [[
                "Nom",
                "Date",
                "Début",
                "Fin",
                "Durée (h)"
             ]]

            #Filter only events related to the product
            for event in events:
                rec_prod_id = event['reccurent_product'].id
                #_logger.info ("ID de RECURRENT_PRODUCT %s" % (rec_prod_id))
                rec_prod= self.env['product.product'].browse(rec_prod_id);

                if rec_prod.id == product.id:

                    start_local = fields.Datetime.context_timestamp(self, event["start"])
                    stop_local = fields.Datetime.context_timestamp(self, event["stop"])

                    date = start_local.strftime("%d/%m/%Y")
                    heure_debut = start_local.strftime("%H:%M")
                    heure_fin = stop_local.strftime("%H:%M")

                    table_data.append([
                        event["name"],
                        date,
                        heure_debut,
                        heure_fin,
                        f"{event['duration']:.2f}"
                    ])

            if len(table_data) == 1:
                content.append(
                    Paragraph(
                        "Aucun événement sur la période.",
                        styles["Normal"]
                    )
                )
            else:
                table = Table(
                    table_data,
                    colWidths=[8*cm, 2.5*cm, 2*cm, 2*cm, 2*cm]
                )

                table.setStyle(TableStyle([
                    # En-tête
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#D9E2F3")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                    ("ALIGN", (1, 0), (-1, 0), "CENTER"),
                    ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),

                    # Corps
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),

                    # Bordures
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("BOX", (0, 0), (-1, -1), 1, colors.black),

                    # Alignements
                    ("ALIGN", (1, 1), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

                    # Lignes alternées
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                        [colors.white, colors.HexColor("#F5F5F5")]),
                ]))

                content.append(table)


                   # content.append(Paragraph(
                    #    f"- {event['name']} | "
                     #   f"{event['start'].strftime('%d/%m/%Y')} "
                      #  f"{event['start'].strftime('%H:%M')} → "
                       # f"{event['stop'].strftime('%H:%M')} "
                        #f"({event['duration']:.2f} h)",
                        #styles["Normal"]
                    #))

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
