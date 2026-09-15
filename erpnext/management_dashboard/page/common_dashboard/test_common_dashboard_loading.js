const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const elements = new Map();
function element(selector) {
    if (!elements.has(selector)) {
        elements.set(selector, {
            find: element,
            appendTo() { return this; },
            on() { return this; },
            text(value) { this.content = value; return this; },
            prop(name, value) { this[name] = value; return this; },
            empty() { this.emptied = true; return this; },
        });
    }
    return elements.get(selector);
}

let calls = 0;
let resolve_request;
let reject_request;
const frappe = {
    pages: { "common-dashboard": {} },
    ui: { make_app_page: () => ({ body: element("body") }) },
    render_template: () => "template",
    call: () => {
        calls++;
        return new Promise((resolve, reject) => {
            resolve_request = resolve;
            reject_request = reject;
        });
    },
};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, "common_dashboard.js"), "utf8"), {
    frappe, $: element, __: text => text,
    document: { hidden: false, addEventListener() {}, removeEventListener() {} },
    setInterval: () => 1, clearInterval() {},
});

(async () => {
    const page = frappe.pages["common-dashboard"];
    const wrapper = {};
    page.on_page_load(wrapper);
    assert.equal(calls, 1, "Page setup must start loading without waiting for page show");
    page.on_page_show(wrapper);
    assert.equal(calls, 1, "The first page show must reuse the in-flight request");
    const controller = wrapper.site_budget_chart;
    const rendered = [];
    controller.render = data => rendered.push(data);
    assert.equal(controller.status.hidden, false, "Loading must be visible while data is pending");
    await controller.refresh();
    assert.equal(calls, 1, "Repeated refreshes must not query concurrently");
    resolve_request({ message: { sites: ["latest"] } });
    await new Promise(setImmediate);
    assert.equal(rendered[0].sites[0], "latest");
    assert.equal(controller.loading, false);

    let destroyed = false;
    const chart = { destroy: () => { destroyed = true; } };
    controller.chart = chart;
    const transient = controller.refresh();
    reject_request({ status: 500 });
    await transient;
    assert.equal(controller.chart, chart, "A temporary error must keep the last chart visible");
    assert(controller.status.content.includes("last loaded values"));
    assert.equal(controller.loading, false, "Failed requests must allow another attempt");

    const denied = controller.refresh();
    reject_request({ status: 403 });
    await denied;
    assert(destroyed, "Revoked permission must remove the financial chart");
    assert.equal(controller.chart, null);
    assert.equal(element(".site-budget-chart").emptied, true);
    controller.stop_auto_refresh();
    console.log("PASS: immediate page load, request deduplication, visible loading, retry and permission handling.");
})().catch(error => { console.error(error); process.exitCode = 1; });
