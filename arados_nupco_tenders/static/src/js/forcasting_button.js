/** @odoo-module */
import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';

export class SaleListController extends ListController {
    setup() {
        super.setup();
    }

    ShowSupplier() {
    this.actionService.doAction({
        type: 'ir.actions.act_window',
        res_model: 'filter.supplier.wizard',
        name: 'Filter by Supplier',
        view_mode: 'form',
        view_type: 'form',
        views: [[false, 'form']],
        target: 'new',
        context: {},  // You can pass any context if needed
    });

}

    ShowBarcode() {
    this.actionService.doAction({
        type: 'ir.actions.act_window',
        res_model: 'filter.barcode.wizard',
        name: 'Filter by Barcode',
        view_mode: 'form',
        view_type: 'form',
        views: [[false, 'form']],
        target: 'new',
        context: {},  // You can pass any context if needed
    });

}

    ShowTender() {
    this.actionService.doAction({
        type: 'ir.actions.act_window',
        res_model: 'filter.tender.wizard',
        name: 'Filter by Tender',
        view_mode: 'form',
        view_type: 'form',
        views: [[false, 'form']],
        target: 'new',
        context: {},  // You can pass any context if needed
    });

}


}

registry.category("views").add("tender_button_in_tree", {
   ...listView,
   Controller: SaleListController,
   buttonTemplate: "button_sale.ListView.Buttons",
});
