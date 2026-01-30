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
                                })
        # sort by date (ascending)
        res = sorted(all_events, key=lambda x: x['start'])
        return res


    @api.onchange('product_id')
    def _onchange_product_compute_hours(self):
        if not self.product_id:
            return

<<<<<<< HEAD
            if not product or not move:
                continue  
=======
        product = self.env['product.product'].browse(self.product_id.id)
        if product.is_product_recurrent:
            _logger.info("Produit recurrent selectionne : %s", product.name)        
>>>>>>> 2fd2036bc81872e200f81e0d0d3162fb85e4aff2

            # retrieve the events between the start and end date of the invoicing period
            move = self.move_id              
         
            events = self.get_events_between_dates(move.billing_start_date, move.billing_end_date)

<<<<<<< HEAD
            if (
                move.billing_start_date
                and move.billing_end_date
                and template.hours_per_day
            ):
                days = (move.billing_end_date - move.billing_start_date).days + 1
                line.quantity = days * template.hours_per_day

    def get_events_between_dates(self):
        self.ensure_one()

        move = self.move_id

        if not move.billing_start_date or not move.billing_end_date:
            return []

        return self.env['calendar.event'].search([
            ('start', '>=', move.billing_start_date),
            ('stop', '<=', move.billing_end_date),
            ('recurring_product_id', '=', self.product_id.id),
        ])
=======
            quantity=0;
            for event in events:
                  _logger.info("Evenement : %s (%s,%s) : start = %s - end = %s (duration = %s)", event['name'],event['id'],event['recurrence_id'],event['start'], event['stop'], event['duration'])
                  quantity+=event['duration']
            self.quantity = quantity
>>>>>>> 2fd2036bc81872e200f81e0d0d3162fb85e4aff2
