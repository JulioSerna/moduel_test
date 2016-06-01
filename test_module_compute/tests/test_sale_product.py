
# coding: utf-8
from openerp.tests.common import TransactionCase
import time


class TestValidateSale(TransactionCase):

    def setUp(self):
        super(TestValidateSale, self).setUp()
        self.sale = self.env['sale.order']
        self.sale_order_line = self.env['sale.order.line']
        self.sale_create_invoice = self.env['sale.advance.payment.inv']
        self.acc_bank_stmt_model = self.env['account.bank.statement']
        self.acc_bank_stmt_line_model = self.env['account.bank.statement.line']
        self.account_receivable_id = self.ref("account.a_recv")

    def test_01_validate_product(self):
        # create sale order
        sale_id = self.sale.create({'partner_id': 18})
        self.sale_order_line.create(
            {
                'order_id': sale_id.id,
                'product_id': 1,
            }
        )
        sale_id.action_button_confirm()

        # create invoice from wizard
        sale_create_inv = self.sale_create_invoice.with_context(
            {'active_id': sale_id.id, 'active_ids': [sale_id.id]}).create(
                {'advance_payment_method': 'all'})
        sale_create_inv.create_invoices()
        sale_id.invoice_ids.signal_workflow('invoice_open')

        for line_invoice in sale_id.invoice_ids.move_id.line_id:
            if line_invoice.account_id.id == self.account_receivable_id:
                line_id = line_invoice
                break

        # create bank statement to pay invoice
        bank_stmt_id = self.acc_bank_stmt_model.create({
            'journal_id': 1,
            'date': time.strftime('%Y') + '-07-01',
        })
        bank_stmt_line_id = self.acc_bank_stmt_line_model.create({
            'name': 'payment',
            'statement_id': bank_stmt_id.id,
            'partner_id': 18,
            'amount': 75,
            'date': time.strftime('%Y') + '-07-01'})

        val = {
            'credit': 75,
            'counterpart_move_line_id': line_id.id,
            'name': line_id.name}

        print '--The checks if invoice was paid must be in False --'
        print sale_id.invoiced2,'invoiced2 before pay invoice -- new api'
        print sale_id.invoiced,'invoiced before pay invoice -- old api'

        # reconcile invoice
        bank_stmt_line_id.process_reconciliation([val])

        print '--The checks if invoice was paid should be in True--'
        print sale_id.invoiced2,'invoiced2 after pay invoice -- new api'
        print sale_id.invoiced,'invoiced after pay invoice  -- old api'
