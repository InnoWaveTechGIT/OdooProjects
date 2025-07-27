/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { parseFloat } from "@web/views/fields/parsers";
import { useState } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { AbstractAwaitablePopup } from "@point_of_sale/app/popup/abstract_awaitable_popup";
import { useAsyncLockedMethod } from "@point_of_sale/app/utils/hooks";
import { Input } from "@point_of_sale/app/generic_components/inputs/input/input";
import { useRef } from "@odoo/owl";


export class CustomButtonPopup extends AbstractAwaitablePopup {
   static template = "pos_order_cashier_report.CustomButtonPopup";
   static defaultProps = {
       closePopup: _t("Cancel"),
       confirmText: _t("Save"),
       title: _t("Customer Details"),
   };
    setup() {
        this.state = useState({
            name: "",
        });
        this.nameInputRef = useRef("name");
    }

     submitForm(event) {
     console.info('SUMBITTTTED*******', this.nameInputRef.el.value);
        const name = this.nameInputRef.el.value;
        this.state.name = name;
        this.props.onSubmit({
            name: name,
        });
        this.props.close();

    }

    close() {
        this.props.close();
    }

    cancel() {
        this.close();
    }
}
