
# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo import Command
from colorama import Fore
from datetime import datetime, date
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError
import pytz
# #############################################################################
class KmPetronadDataInputWizard(models.TransientModel):
    _name = 'km_petronad_import.data_input.wizard'
    _description = 'Data input Wizard'

    # todo: fix timezone
    start_datetime = fields.Datetime(required=True,default=lambda self: datetime.now().replace(hour=0, minute=0, second=0) - timedelta(hours=3.5) )
    end_datetime = fields.Datetime(required=True, default=lambda self: datetime.now().replace(hour=23, minute=59, second=59) - timedelta(hours=3.5) )

    # start_datetime = fields.Datetime(required=True,default=lambda self: datetime.now().replace(hour=0, minute=0, second=0).astimezone(pytz.timezone(self.env.context.get("tz"))).replace(tzinfo=None) )
    # end_datetime = fields.Datetime(required=True, default=lambda self: datetime.now().replace(hour=23, minute=59, second=59).astimezone(pytz.timezone(self.env.context.get("tz"))).replace(tzinfo=None) )

    # end_datetime = fields.Datetime(required=True, default=lambda self: datetime.now(pytz.timezone(self.env.context.get('tz', 'Asia/Tehran'))))
    company = fields.Many2one('res.company', required=1, default=lambda self: self.env.user.company_id.id)
    production_unit = fields.Many2one('km_petronad_import.production_unit', default=lambda self: self.search([('company', '=', self.env.user.company_id.id)], limit=1))
    fluid = fields.Many2one('km_petronad_import.fluids', required=True, )
    tank = fields.Many2one('km_petronad_import.storage_tanks', required=True, )
    tank_capacity = fields.Integer(related='tank.capacity')
    tank_amount = fields.Integer(related='tank.amount')
    tank2 = fields.Many2one('km_petronad_import.storage_tanks', )
    tank2_capacity = fields.Integer(related='tank2.capacity')
    tank2_amount = fields.Integer(related='tank2.amount')
    # todo: operation needed to be updated based on fluid_type of the fluid:
    #   feed -> feed_receive, feed_usage, sending, movement
    #   product -> production, sending, movement
    # operation = fields.Selection([
    #                                 ('production', 'Production'),
    #                                 ('feed_receive', 'Feed Receive'),
    #                                 ('feed_usage', 'Feed Usage'),
    #                                 ('sending', 'Sending'),
    #                                 ('movement', 'Movement'),
    #                                 ], default='production', require=True)
    operation = fields.Many2one('km_petronad_import.tank_operations', required=True,)
    operation_code = fields.Char(related='operation.code')
    amount = fields.Integer(require=True)
    sending_types = fields.Selection([('sale', 'Sale'), ('transfer', 'Transfer')], default='sale',)

    destination = fields.Many2one('res.partner')


    #
    # #############################################################################
    def process_data(self):
        # print(f'ddddddddddddddddd>\n {self.operation.code}   {self.fluid.fluid_type} \n')
        read_form = self.read()[0]
        data = {'form_data': read_form}
        print(f'PROCESS:\n {read_form}')
        if self.operation.code in [ 'feed_usage',]  :
            if self.fluid.fluid_type == 'feed':
                self.tank.write({'amount': -1 * self.amount + self.tank.amount})
            else:
                raise ValidationError(_(f'Not allowed operation'))

        elif self.operation.code in [ 'feed_receive', ]:
            if self.fluid.fluid_type == 'feed':
                self.tank.write({'amount': self.amount + self.tank.amount})
            else:
                raise ValidationError(_(f'Not allowed operation'))
        #     crate feed receive record

        elif self.operation.code in [ 'production', ]:
        #     create production record
            if self.fluid.fluid_type == 'product':
                self.tank.write({'amount': self.amount + self.tank.amount})
            else:
                raise ValidationError(_(f'Not allowed operation'))

        elif self.operation.code in [ 'sending',] :
            self.tank.write({'amount': -1 * self.amount + self.tank.amount})

        elif self.operation.code == 'movement':
            self.tank.write({'amount': -1 * self.amount + self.tank.amount})
            self.tank2.write({'amount':  self.amount + self.tank2.amount})
    #         todo: create a movement record
        else:
            raise ValidationError(_(f'Not allowed operation'))


    @api.onchange('amount')
    def amount_changed(self):
        if self.operation.code in [ 'feed_usage', 'sending', 'movement'] and self.amount > self.tank.amount:
            raise ValidationError(_(f'There is no enough in the tank {self.tank.name}'))

        if self.operation.code in [ 'feed_receive', ] and self.amount > self.tank.capacity - self.tank.amount:
            raise ValidationError(_(f'There is no free space in tank {self.tank.name}'))

        if self.operation.code in [ 'movement', ] and self.amount > self.tank2.capacity - self.tank2.amount:
            raise ValidationError(_(f'There is no free space in tank {self.tank2.name}'))




    @api.onchange('fluid')
    def fluid_changed(self):
        self.tank =  self.tank.search([('fluid', '=', self.fluid.id)],limit=1) or False
        self.operation =  self.operation.search([('fluid', 'in', self.fluid.id)],limit=1) or False

    #     if self.fluid.fluid_type == 'feed':
    #         self.operation.selection =  [('feed_usage', 'Feed Usage'),
    #                          ('feed_receive', 'Feed Receive'),
    #                          ('sending', 'Sending'),
    #                          ('movement', 'Movement'),]
    #     elif self.fluid.fluid_type == 'product':
    #         self.operation =   [ ('production', 'Production'),
    #                          ('sending', 'Sending'),
    #                          ('movement', 'Movement'),]
    #     else:
    #         self.operation =   []


    @api.onchange('operation')
    def operation_changed(self):
        print(f'...........>>>\n operation: {self.operation} <<< .....................')


    @api.onchange('company')
    def company_changed(self):
        self.production_unit =  self.production_unit.search([('company', '=', self.company.id)],limit=1) or False
        format = ""
        # print(f'>>>>>________>>>>>  {datetime.now(pytz.timezone("Asia/Tehran")).replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")}')
        # print(f'>>>>>________>>>>>    {datetime.now().replace(hour=0, minute=0, second=0).astimezone(pytz.timezone(self.env.context.get("tz"))).replace(tzinfo=None)}')
        # print(f'>>>>>________>>>>>    {datetime.now().replace(hour=23, minute=59, second=59).astimezone(pytz.timezone(self.env.context.get("tz"))).replace(tzinfo=None)}')
        # print(f'>>>>>________>>>>>    {datetime.now().replace(hour=0, minute=0, second=0) - timedelta(hours=3.5)}')
        # print(f'>>>>>________>>>>>    {datetime.now().replace(hour=23, minute=59, second=59) - timedelta(hours=3.5)}')
        # print(f'>>>>>________>>>>>    {datetime.now().replace(hour=23, minute=59, second=59)}')


    @api.onchange('production_unit')
    def production_unit_changed(self):
        self.fluid =  self.fluid.search([('production_units', 'in', self.production_unit.id)],limit=1) or False



