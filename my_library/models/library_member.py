from odoo import fields, models

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
    # You could also add a Many2many field to link books if needed later
    # borrowed_book_ids = fields.Many2many(
    #     'library.book',
    #     string='Borrowed Books',
    # )

    # Optional: Add a computed field or constraint later if needed
    # _sql_constraints = [
    #     ('unique_email', 'unique(email)', 'Email must be unique!'),
    # ]

    # Optional: Override name_get for better display in relational fields
    def name_get(self):
        result = []
        for record in self:
            result.append((record.id, f"{record.name} ({record.email or 'No Email'})"))
        return result