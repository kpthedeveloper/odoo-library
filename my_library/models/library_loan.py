# my_library/models/library_loan.py
# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import timedelta, date # Import timedelta and date for calculations

class LibraryLoan(models.Model):
    _name = 'library.loan'
    _description = 'Library Book Loan'
    _rec_name = 'display_name' # Use a computed field for record name
    _inherit = ['mail.thread', 'mail.activity.mixin'] # Keep mail features for chatter and activities

    # Relational fields
    book_id = fields.Many2one(
        'library.book',
        string='Book',
        required=True,
        ondelete='restrict', # Prevent deleting a book if it has active loans
        # domain=[('is_available', '=', True)] # Keep commented if 'is_available' not on library.book yet
    )
    member_id = fields.Many2one(
        'library.member',
        string='Member',
        required=True,
        ondelete='restrict' # Prevent deleting a member if they have active loans
    )

    # Date fields
    loan_date = fields.Date(string='Loan Date', default=fields.Date.today(), required=True)
    
    # Expected Return Date - This is now a computed field
    return_date = fields.Date(
        string='Expected Return Date',
        compute='_compute_expected_return_date', # Method to compute this field
        store=True, # Store the computed value in DB for searching/filtering
        help="Calculated date when the book is expected to be returned (Loan Date + 30 days)."
    )

    # New field for the actual Date Returned by the member
    date_returned = fields.Date(
        string='Date Returned',
        copy=False, # Don't copy this field when duplicating a record
        help="The actual date the book was returned by the member."
    )

    # State field to track the loan status
    state = fields.Selection(
        [('draft', 'Draft'),
         ('loaned', 'Loaned'),
         ('returned', 'Returned'),
         ('cancelled', 'Cancelled'),
         ('overdue', 'Overdue')],
        string='Status',
        default='draft',
        required=True,
        copy=False, # Don't copy this field when duplicating a record
        tracking=True, # Track changes to this field for chatter
        help="The status of the book loan."
    )

    # Computed field for display name in relational fields
    @api.depends('book_id', 'member_id', 'loan_date')
    def _compute_display_name(self):
        """
        Generates a readable name for the loan record, useful in related records.
        """
        for record in self:
            record.display_name = f"{record.book_id.name or 'N/A'} loaned to {record.member_id.name or 'N/A'} on {record.loan_date or 'N/A'}"

    # Computed method for Expected Return Date
    @api.depends('loan_date')
    def _compute_expected_return_date(self):
        """
        Computes the expected return date based on the loan date + 30 days.
        """
        for record in self:
            if record.loan_date:
                record.return_date = record.loan_date + timedelta(days=30)
            else:
                record.return_date = False # Set to False if loan_date is not set

    # Indexes for database optimization and partial unique constraints
    # This correctly implements the "a book can only be loaned once at a time" rule.
    _indexes = [
        # This creates a unique index on 'book_id' ONLY for records where 'state' is 'loaned'.
        # This prevents the same book from being loaned out multiple times simultaneously.
        ('library_loan_unique_loan_per_book_idx', 'unique (book_id) WHERE state = \'loaned\'', 'unique (book_id) on state = \'loaned\'')
    ]

    # Constraints and business logic (Python-level validation)
    @api.constrains('loan_date', 'date_returned')
    def _check_dates(self):
        """
        Ensures that the actual return date (if set) is not earlier than the loan date.
        """
        for record in self:
            if record.date_returned and record.date_returned < record.loan_date:
                raise ValidationError(_("Date Returned cannot be earlier than Loan Date."))

    # Action methods (buttons in the UI to change state)
    def action_loan(self):
        """
        Changes the loan state from 'draft' to 'loaned'.
        """
        self.ensure_one() # Ensures the method is called on a single record
        if self.state == 'draft':
            self.state = 'loaned'
        else:
            raise ValidationError(_("Only draft loans can be marked as loaned."))

    def action_return(self):
        """
        Marks the loan as returned and sets the actual return date to today.
        """
        self.ensure_one()
        if self.state in ('loaned', 'overdue'): # Can return if currently loaned or overdue
            self.state = 'returned'
            self.date_returned = fields.Date.today() # Set the actual return date to today
        else:
            raise ValidationError(_("Only loaned or overdue books can be marked as returned."))

    def action_cancel(self):
        """
        Cancels the loan and clears the actual return date if set.
        """
        self.ensure_one()
        if self.state in ('draft', 'loaned', 'overdue'):
            self.state = 'cancelled'
            self.date_returned = False # Clear date_returned if cancelled
        else:
            raise ValidationError(_("Only draft, loaned, or overdue books can be cancelled."))

    def action_set_to_draft(self):
        """
        Sets a cancelled loan back to draft state and clears the actual return date.
        """
        self.ensure_one()
        if self.state == 'cancelled':
            self.state = 'draft'
            self.date_returned = False # Clear date_returned if moving back to draft
        else:
            raise ValidationError(_("Only cancelled loans can be set back to draft."))