from odoo import models, fields, api
import pytz

from datetime import datetime

import logging

_logger = logging.getLogger(__name__)

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    def get_events_between_dates(self, start_date, end_date):
        
        # date conversion
        start_datetime = fields.Datetime.to_datetime(start_date)
        end_datetime = fields.Datetime.to_datetime(end_date)
        local_tz = pytz.timezone('Europe/Paris')
        start_local = local_tz.localize(start_datetime)
        end_local = local_tz.localize(end_datetime)
            
        start_utc = start_local.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
        end_utc = end_local.astimezone(pytz.UTC).strftime("%Y-%m-%d %H:%M:%S")
        
        # return a list of info about event in the given period
        all_events = []

        non_recurrent_events = self.env['calendar.event'].search([
            ('start', '>=', start_utc),
            ('stop', '<=', end_utc),
            ('recurrency', '=', False),
        ])

        # add non recurrent event in the list to return
        for event in non_recurrent_events:
            all_events.append({
                'id': event.id,
                'name': event.name,
                'start': event.start,
                'stop': event.stop,
                'duration' : event.duration,
                'recurrence_id': event.id,
                'reccurent_product':event.recurring_product_id,
            })

        # add recurring event in the list to return
        recurrent_events = self.env['calendar.event'].search([
            ('recurrency', '=', True),
        ])

        # search occurrences in the given period
        for event in recurrent_events:
            if event.recurrence_id:
                event_occurrences = event.recurrence_id._get_occurrences(start_datetime)
                for occurrence in event_occurrences:
                    if start_datetime <= occurrence <= end_datetime:
                        # prevent from doublon
                        occurrence_stop = fields.Datetime.add(occurrence, seconds=event.duration * 3600)
                   
                        if not any(e['recurrence_id'] ==event.recurrence_id.id and e['start'] == occurrence and e['stop'] ==e['stop'] == occurrence_stop for e in all_events):
                            all_events.append({
                                'id': event.id,
                                'name': event.name,
                                'start': occurrence,
                                'stop': fields.Datetime.add(occurrence, seconds=event.duration * 3600),
                                'duration': event.duration,
                                'recurrence_id': event.recurrence_id.id,
                                'reccurent_product':event.recurring_product_id,
                                })
        # sort by date (ascending)
        res = sorted(all_events, key=lambda x: x['start'])
        return res


    def _get_product_quantity (self,start_date,end_date):
        """Calcule la quantité à facturer pour une ligne de facture donnée, à partir des
        événements calendrier du produit récurrent sur la période donnée."""
                
        self.ensure_one()

        if not self.product_id or not start_date or not end_date:
            return self.quantity
        
        product = self.env['product.product'].browse(self.product_id.id)
        _logger.info ("ID de RECURRENT_PRODUCT %s" % (product.id))
        
        if not product.is_product_recurrent:
            return self.quantity
         
        events = self.get_events_between_dates(start_date, end_date)
        
        quantity = 0
        for event in events:
            rec_prod_id = event['reccurent_product'].id
            rec_prod = self.env['product.product'].browse(rec_prod_id)
            _logger.info ("EVENT FOR A RECURRENT_PRODUCT %s" % (rec_prod_id))
            if rec_prod.id == product.id:
                    quantity+=event['duration']
        
        return quantity


    @api.onchange('product_id')
    def _onchange_product_compute_hours(self):
        if not self.product_id:
            return

        product = self.env['product.product'].browse(self.product_id.id)
        if product.is_product_recurrent:
            # retrieve the events between the start and end date of the invoicing period
            move = self.move_id  
            self.quantity = self._get_product_quantity(move.billing_start_date, move.billing_end_date)
