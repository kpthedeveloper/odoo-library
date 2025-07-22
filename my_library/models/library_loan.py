# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError

class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Library Book Loan'
    _rec_name = 'display_name' # Use a computed field for record name

    # Relational fields
    book_id = fields.Many2one(
        'library.book',
        string='Book',
        required=True,
        ondelete='restrict', # Prevent deleting a book if it has active loans
        domain=[('is_available', '=', True)] # Filter for available books (we'll add is_available later)
    )
    member_id = fields.Many2one(
        'library.member',
        string='Member',
        required=True,
        ondelete='restrict' # Prevent deleting a member if they have active loans
    )

    # Date fields
    loan_date = fields.Date(string='Loan Date', default=fields.Date.today(), required=True)
    return_date = fields.Date(string='Return Date')

    # State field to track the loan status
    state = fields.Selection(
        [('draft', 'Draft'),
         ('loaned', 'Loaned'),
         ('returned', 'Returned'),
         ('cancelled', 'Cancelled')],
        string='Status',
        default='draft',
        required=True,
        copy=False, # Don't copy this field when duplicating a record
        help="The status of the book loan."
    )

    # Computed field for display name in relational fields
    @api.depends('book_id', 'member_id', 'loan_date')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.book_id.name} loaned to {record.member_id.name} on {record.loan_date}"

    # Constraints and business logic
    _sql_constraints = [
        ('unique_loan_per_book', 'unique(book_id, state) WHERE state = \'loaned\'',
         'A book can only be loaned once at a time.'),
    ]

    @api.constrains('loan_date', 'return_date')
    def _check_dates(self):
        for record in self:
            if record.return_date and record.return_date < record.loan_date:
                raise ValidationError(_("Return Date cannot be earlier than Loan Date."))

    # Action methods (buttons in the UI)
    def action_loan(self):
        for record in self:
            if record.state == 'draft':
                record.state = 'loaned'
            else:
                raise ValidationError(_("Only draft loans can be marked as loaned."))

    def action_return(self):
        for record in self:
            if record.state == 'loaned':
                record.state = 'returned'
                record.return_date = fields.Date.today()
            else:
                raise ValidationError(_("Only loaned books can be marked as returned."))

    def action_cancel(self):
        for record in self:
            if record.state in ('draft', 'loaned'):
                record.state = 'cancelled'
            else:
                raise ValidationError(_("Only draft or loaned books can be cancelled."))

    def action_set_to_draft(self):
        for record in self:
            if record.state == 'cancelled':
                record.state = 'draft'
                record.return_date = False # Clear return date if moving back to draft
            else:
                raise ValidationError(_("Only cancelled loans can be set back to draft."))