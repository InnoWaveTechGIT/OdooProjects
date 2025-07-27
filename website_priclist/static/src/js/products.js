odoo.define('website_priclist.pricelist_selector', function (require) {
    "use strict";

    var Dialog = require('web.Dialog');
    var rpc = require('web.rpc');
    var _t = require('web.core')._t; // Assuming this is for translations

    document.addEventListener('DOMContentLoaded', () => {
        const pricelistSelectorButton = document.getElementById('pricelist_selector_button');

        pricelistSelectorButton.addEventListener('click', async () => {
            const dialogContent = document.createElement('div');
            dialogContent.innerHTML = await web.template.qweb.get_template('website_priclist.pricelist_selection_dialog');

            const dialog = new Dialog(pricelistSelectorButton, {
                title: _t("Select Pricelist"), // Assuming _t is for translations
                size: 'medium',
                $content: dialogContent,
                buttons: [{
                    text: _t("Confirm"), // Assuming _t is for translations
                    classes: 'btn-primary',
                    click: async () => {
                        const selectedPricelistId = document.getElementById('pricelist_selector').value;
                        const products = await rpc.query({
                            model: 'product.template',
                            method: 'search_read',
                            args: [[['pricelist_id', '=', selectedPricelistId]]],
                            fields: ['name', 'image_small', 'list_price']
                        });

                        console.log(products);
                        // Implement logic to display products on the website
                        dialog.close();
                    }
                }]
            });

            dialog.open();
        });
    });

}, []); // Add the empty dependency array here
