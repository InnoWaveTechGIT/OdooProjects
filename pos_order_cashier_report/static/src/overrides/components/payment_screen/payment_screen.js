/** @odoo-module */
import { CustomButtonPopup } from "@pos_order_cashier_report/app/invoice/invoice_popup/invoice_popup";
import { PaymentScreen } from "@point_of_sale/app/screens/payment_screen/payment_screen";
import { patch } from "@web/core/utils/patch";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { _t } from "@web/core/l10n/translation";
import { CashMovePopup } from "@point_of_sale/app/navbar/cash_move_popup/cash_move_popup";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";

var invoice_referance = '' ;
patch(PaymentScreen.prototype, {

        async openinvoicepopup() {
//        console.info('TOGGLE IS INVOICE(INH) ------',this.pos.orders);
        const result = await this.popup.add(CustomButtonPopup, {
            title: _t("Select the Invoice to settle the due"),
            confirmPopup: _t("Confirm"),
            closePopup: _t("Close"),
            onSubmit: (data) => {
//                console.log('Form submitted with:', data);
                invoice_referance = data
            }
        });
         console.log('Form Full with:',invoice_referance);

        if (invoice_referance.name) {
                if (this.pos.orders.length > 0) {
                const lastOrder = this.pos.orders[this.pos.orders.length - 1];
                lastOrder.posreferance = invoice_referance.name;
                console.log('Invoice number is  :', lastOrder.posreferance);
                }
        }else{

            console.log('Form Closed with:');

        }
    },

});
