from openerp import models, fields, api
from datetime import datetime, timedelta

class sale_order_expiration_reminder(models.Model):
    _inherit = 'sale.order'
    
    consultancy_expiration_selection = fields.Selection(selection=[('not_applicable', 'Not Applicable'), ('in_progress', 'In Progress'), ('to_renew', 'To Renew'),('closed','Closed')], string='Expiration Management', default='not_applicable')
    consultancy_expiration_date = fields.Date(string='Expiration date')
    consultancy_expiration_in_days = fields.Integer(string='Contract consultancy expiration in days', compute='_consultancy_expiration_in_days')

    @api.depends('consultancy_expiration_date')
    def _consultancy_expiration_in_days(self):
        date_format = "%Y-%m-%d"
        now = datetime.now()
        for sale_order in self:
            consultancy_expiration_date = datetime.strptime(self.consultancy_expiration_date, date_format)
            date_delta = consultancy_expiration_date - now
            sale_order.consultancy_expiration_in_days = date_delta.days

    @api.model
    def _cron_sale_order_consultancy_expiration_reminder(self):
        if self.env.context is None:
            self.env.context = {}
        context = self.env.context
        
        #structure: {'user_id': {'old/new/future': {'partner_id': [account_obj()]}}}
        remind = {}

        def fill_remind(key, domain, write_to_renew=False):
            base_domain = [
                ('state', '=', 'sale'),
                ('consultancy_expiration_selection', '=', 'active')
                ('partner_id', '!=', False), #Customer
                ('user_id', '!=', False),    #Salesperson
                ('user_id.email', '!=', False),
            ]
            base_domain.extend(domain)

            for sale_order in self.search(base_domain, order='name asc'):
                if write_to_renew:
                    sale_order.consultancy_expiration_selection = 'to_renew'
                remind_user = remind.setdefault(sale_order.user_id.id, {})
                remind_type = remind_user.setdefault(key, {})
                remind_partner = remind_type.setdefault(sale_order.partner_id, []).append(sale_order)

        # Already expired
        fill_remind("old", [('consultancy_expiration_selection', 'in', ['to_renew'])])

        # Expires now
        fill_remind("new", [('consultancy_expiration_selection', 'in', ['in_progress']), '|', '&', ('consultancy_expiration_date', '!=', False), ('consultancy_expiration_date', '<=', time.strftime('%Y-%m-%d'))], True)

        # Expires in less than 30 days
        fill_remind("future", [('consultancy_expiration_selection', 'in', ['in_progress']), ('consultancy_expiration_date', '!=', False), ('consultancy_expiration_date', '<', (datetime.now() + timedelta(30)).strftime("%Y-%m-%d"))])

        #For the url in  generated email linked to the sale orders list (menuitem)
        context['base_url'] = self.env["ir.config_parameter"].get_param("web.base.url")
        context['action_id'] = self.env["ir.model.data"].get_object_reference('sale', 'action_orders')[1]
        
        template_id = self.env["ir.model.data"].get_object_reference('sale_order_expiration_and_reminder', 'sale_order_expiration_reminder_cron_email_template')[1]
        
        for user_id, data in remind.items():
            context["data"] = data
            self.env["email.template"].send_mail(template_id, user_id, force_send=True, context=context)

        return True