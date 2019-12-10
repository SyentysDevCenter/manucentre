odoo.define('pos_licences.pos_licences', function(require) {
    "use strict";

    var models = require('point_of_sale.models');

    models.load_fields('res.partner',
                    ['hunting_licence_number','hunting_licence_date','hunting_licence_validity','hunting_oncfs','hunting_state',
                    'shooting_licence','shooting_licence_validity','shooting_club_number','shooting_club_name',
                    'balltrap_licence','balltrap_licence_validity','balltrap_club_number','balltrap_club_name']
                    );



});