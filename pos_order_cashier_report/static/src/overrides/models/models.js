/** @odoo-module */
import { useService } from "@web/core/utils/hooks";
import { Order, Orderline, Payment } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";
import { Component } from "@odoo/owl";
import { omit } from "@web/core/utils/objects";


import { constructFullProductName, random5Chars, uuidv4, qrCodeSrc } from "@point_of_sale/utils";
// FIXME POSREF - unify use of native parseFloat and web's parseFloat. We probably don't need the native version.
import { parseFloat as oParseFloat } from "@web/views/fields/parsers";
import {
    formatDate,
    formatDateTime,
    serializeDateTime,
    deserializeDate,
    deserializeDateTime,
} from "@web/core/l10n/dates";
import {
    formatFloat,
    roundDecimals as round_di,
    roundPrecision as round_pr,
    floatIsZero,
} from "@web/core/utils/numbers";
import { ErrorPopup } from "@point_of_sale/app/errors/popups/error_popup";
import { ConfirmPopup } from "@point_of_sale/app/utils/confirm_popup/confirm_popup";
import { _t } from "@web/core/l10n/translation";
import { renderToElement } from "@web/core/utils/render";

const { DateTime } = luxon;



patch(Order.prototype, {
        setup() {
        super.setup(...arguments);
//        console.info("setup called from child",(this.pos_session_id)  +  (this.sequence_number)  );
         this.posreferance = null;
    },
     export_for_printing() {
        // If order is locked (paid), the 'change' is saved as negative payment,
        // and is flagged with is_change = true. A receipt that is printed first
        // time doesn't show this negative payment so we filter it out.

        const paymentlines = this.paymentlines
            .filter((p) => !p.is_change)
            .map((p) => p.export_for_printing());
//             console.info(" innnnnnhhhhprinnnnnting22222222222222",this);

        return {
            orderlines: this.orderlines.map((l) => omit(l.getDisplayData(), "internalNote")),
            paymentlines,
            amount_total: this.get_total_with_tax(),
            total_without_tax: this.get_total_without_tax(),
            amount_tax: this.get_total_tax(),
            total_paid: this.get_total_paid(),
            total_discount: this.get_total_discount(),
            rounding_applied: this.get_rounding_applied(),
            tax_details: this.get_tax_details(),
            change: this.locked ? this.amount_return : this.get_change(),
            name: this.get_name(),
            invoice_name: this.posreferance,
            invoice_id: null, //TODO
            cashier: this.cashier?.name,
            date: formatDateTime(this.date_order),
            pos_qr_code:
                this.pos.company.point_of_sale_use_ticket_qr_code &&
                (this.finalized || ["paid", "done", "invoiced"].includes(this.state)) &&
                qrCodeSrc(
                    `${this.pos.base_url}/pos/ticket/validate?access_token=${this.access_token}`
                ),
            ticket_code:
                this.pos.company.point_of_sale_ticket_unique_code &&
                this.finalized &&
                this.ticketCode,
            base_url: this.pos.base_url,
            footer: this.pos.config.receipt_footer,
            // FIXME: isn't there a better way to handle this date?
            shippingDate:
                this.shippingDate && formatDate(DateTime.fromJSDate(new Date(this.shippingDate))),
            headerData: {
                ...this.pos.getReceiptHeaderData(this),
                trackingNumber: this.trackingNumber,
            },
        };
    },
});
