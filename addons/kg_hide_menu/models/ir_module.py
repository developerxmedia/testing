# # -*- coding: utf-8 -*-

# # Klystron Global LLC
# # Copyright (C) Klystron Global LLC
# # All Rights Reserved
# # https://www.klystronglobal.com/


# from odoo import models, api, tools


# class Menu(models.Model):
#     _inherit = 'ir.ui.menu'

#     @api.model
#     @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
#     def _visible_menu_ids(self, debug=False):
#         menus = super(Menu, self)._visible_menu_ids(debug)
#         if self.env.user.hide_menu_access_ids and not self.env.user.has_group('base.group_system'):
#             for rec in self.env.user.hide_menu_access_ids:
#                 menus.discard(rec.id)
#             return menus
#         return menus

from odoo import models, api, tools


class Menu(models.Model):
    _inherit = 'ir.ui.menu'

    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        menus = super(Menu, self)._visible_menu_ids(debug)
        # Extra safeguard: ensure base.group_no_one exists before filtering
        no_one_group = self.env.ref('base.group_no_one', raise_if_not_found=False)
        if not no_one_group:
            return menus  # skip filtering to avoid crash

        if self.env.user.hide_menu_access_ids and not self.env.user.has_group('base.group_system'):
            for rec in self.env.user.hide_menu_access_ids:
                menus.discard(rec.id)
        return menus
