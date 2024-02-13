# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import date, datetime
import jdatetime
import json



class KmPetronadShutdownInherit(models.Model):
    _inherit = 'km_petronad.shutdown'

    j_data_date = fields.Char()

    def j_data_date_converter(self):
        active_ids = self.env.context.get('active_ids')
        production_records = self.browse(active_ids)
        for record in production_records:
            jdate = record.j_data_date.split('/')
            rec_date = jdatetime.date(int(jdate[0]), int(jdate[1]), int(jdate[2]),).togregorian()
            record.write({'shutdown_date': rec_date})





