# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
import jdatetime
import json



class KmPetronadProductionRecordInherit(models.Model):
    _inherit = 'km_petronad.production_record'

    j_data_date = fields.Char()

    def j_data_date_converter(self):
        active_ids = self.env.context.get('active_ids')
        production_records = self.browse(active_ids)
        for record in production_records:
            jdate = record.j_data_date.split('/')
            rec_date = jdatetime.date(int(jdate[0]), int(jdate[1]), int(jdate[2]),).togregorian()
            record.write({'data_date': rec_date})

    def amount_converter(self):
        active_ids = self.env.context.get('active_ids')
        production_records = self.browse(active_ids)
        for record in production_records:
            amount = -1 * record.amount if record.amount < 0 else record.amount
            record.write({'amount': amount})


            # print(f'\n production_records: \n {record.j_data_date}  :  {rec_date}')


