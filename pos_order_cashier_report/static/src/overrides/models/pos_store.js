/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

var order_referance_data_name = '' ;
var order_referance_data_name22 = '' ;
patch(PosStore.prototype, {
        async setup(...args) {
            console.info("setup child ");
            return await super.setup(...args);
        },
        getReceiptHeaderData(order) {
        const result = super.getReceiptHeaderData(...arguments);
        // console.info('oooooooooooooorder', order.posreferance)
        if(order)
        {
                result.partner = order.get_partner()?.name;
                if (order.posreferance){
                    result.invoice_name = order.posreferance;
                    console.info('reeeeeeeeeef ',result );
                 }

        }
     return result;
    },
});
