# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    name = fields.Char('Title', required=True)
    author = fields.Char('Author')
    isbn = fields.Char('ISBN', help="The International Standard Book Number")
    publication_date = fields.Date('Publication Date')
    publisher_id = fields.Many2one('res.partner', string='Publisher')
    librarian_notes = fields.Text('Librarian Notes')

    # New field: Check if the book is currently available for loan
    is_available = fields.Boolean(
        string='Available',
        compute='_compute_is_available',
        store=False # No need to store this in DB, compute on the fly
    )

    # One2many field to link to loans (optional, but useful for seeing book's loan history)
    loan_ids = fields.One2many(
        'library.loan',
        'book_id',
        string='Loans'
    )

    # Computed method for is_available
    @api.depends('loan_ids.state') # Recalculate if any related loan's state changes
    def _compute_is_available(self):
        for book in self:
            # A book is available if it has no 'loaned' or 'draft' loans
            # Or if all its loans are 'returned' or 'cancelled'
            book.is_available = not any(
                loan.state in ('draft', 'loaned') for loan in book.loan_ids
            )

    _sql_constraints = [
        ('unique_isbn', 'UNIQUE(isbn)', 'ISBN must be unique.'),
    ]