/** @odoo-module */
import { ListController } from "@web/views/list/list_controller";
import { registry } from '@web/core/registry';
import { listView } from '@web/views/list/list_view';

export class SaleListController extends ListController {
    setup() {
        super.setup();
    }

    onTestClick() {
    this.actionService.doAction({
        type: 'ir.actions.act_window',
        res_model: 'add.month.wizard',
        name: 'Set AVG Sales Month',
        view_mode: 'form',
        view_type: 'form',
        views: [[false, 'form']],
        target: 'new',
        context: {},  // You can pass any context if needed
    });

}
ShowVendor() {
    this.actionService.doAction({
        type: 'ir.actions.act_window',
        res_model: 'add.vendor.wizard',
        name: 'Set Vendor',
        view_mode: 'form',
        view_type: 'form',
        views: [[false, 'form']],
        target: 'new',
        context: {},  // You can pass any context if needed
    });

}
onTestClick1() {
    this.actionService.doAction({
        type: 'ir.actions.act_window',
        res_model: 'add.goal.wizard',
        name: 'Set MRD Goal',
        view_mode: 'form',
        view_type: 'form',
        views: [[false, 'form']],
        target: 'new',
        context: {},  // You can pass any context if needed
    });

}

}

registry.category("views").add("button_in_tree", {
   ...listView,
   Controller: SaleListController,
   buttonTemplate: "button_sale.ListView.Buttons",
});
