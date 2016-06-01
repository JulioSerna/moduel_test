# coding: utf-8
from openerp import models, fields, api


class SaleOrder(models.Model):

    _inherit = 'sale.order'

    invoiced2 = fields.Boolean(
        string='invoice 2',
        compute='_invoiced2'
    )

    @api.multi
    def _invoiced2(self):
        for sale in self:
            sale.invoiced2 = True
            invoice_existence = False
            for invoice in sale.invoice_ids:
                if invoice.state!='cancel':
                    invoice_existence = True
                    if invoice.state != 'paid':
                        sale.invoiced2 = False
                        break
            if not invoice_existence or sale.state == 'manual':
                sale.invoiced2 = False
