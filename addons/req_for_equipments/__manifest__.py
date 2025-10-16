{
    "name": "Request For Equipments",
    "version": "1.0",
    "author": "Your Company",
    "category": "Tools",
    "summary": "Manage equipment requests",
    'website':'www.google.com',
    'depends':['sale','mail','project'],
    'data':[
        'security/ir.model.access.csv', 
        'security/approval.xml',
        'views/projects.xml',
        'views/req_for_equipments.xml',
        'views/product_inherit.xml',
        
    ],
    'installable':True,
    'application':True,
    'auto_install':False    
}