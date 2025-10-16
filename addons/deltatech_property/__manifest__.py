# -*- coding: utf-8 -*-
# ©  2015-2019 Deltatech
#              Dorin Hongu <dhongu(@)gmail(.)com
# See README.rst file on addons root folder for license details

{
    "name": "Property Management",
    'version': '17.0.1.0.0',
    "author": "Terrabit, Dorin Hongu",
    "website": "https://www.terrabit.ro",

    "category": "Property",
    "depends": [
        'mail',
        'maintenance','asset','contacts','kanban_draggable','serviceprovider','hr',
    ],
    "license": "AGPL-3",
    "data": [
        'views/property_menu_view.xml',
        'views/property_config_view.xml',
        'views/property_land_view.xml',
        'views/property_building_view.xml',
        'views/property_room_view.xml',
        'data/data.xml',
        # 'data/res.country.state.csv',
        'security/ir.model.access.csv',
        'views/propertytype.xml',
         'views/propertyfloor.xml',
        'views/buildingareatype.xml',
        #'views/masterproperty.xml',
          'views/facility_master.xml',
           'views/floortypes.xml',
           'views/roomtypes.xml',
             'views/sericetypes.xml',
             'views/hrmodel.xml',
             'security/security.xml'
    ],
    'application': True,
    "images": ['static/description/main_screenshot.png','static/description/main_screenshot.svg'],
    "installable": True,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
