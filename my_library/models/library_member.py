# my_library/models/library_member.py
# -*- coding: utf-8 -*-

from odoo import fields, models, api # Ensure 'api' is imported as good practice, though not strictly used for this field

class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Library Member'

    name = fields.Char(string='Name', required=True)
    email = fields.Char(string='Email')
    phone = fields.Char(string='Phone')
    address = fields.Text(string='Address')
    membership_status = fields.Selection(
        [('active', 'Active'), ('inactive', 'Inactive'), ('pending', 'Pending')],
        string='Membership Status',
        default='pending',
        required=True
    )
    membership_tier = fields.Selection(
        [('bronze', 'Bronze'), ('silver', 'Silver'), ('gold', 'Gold')],
        string='Membership Tier',
        default='bronze',
        required=True
    )
    # NEW FIELD: One2Many relationship to library.loan
    loan_ids = fields.One2many(
        'library.loan',         # The target model (library.loan)
        'member_id',            # The field on the 'library.loan' model that links back to 'library.member'
        string='Current Loans'  # Label for the field in the UI
    )

    # Optional: Override name_get for better display in relational fields
    @api.depends('name', 'email') # Add fields to depends for computed name
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, f"{record.name} ({record.email or 'No Email'})"))
        return result