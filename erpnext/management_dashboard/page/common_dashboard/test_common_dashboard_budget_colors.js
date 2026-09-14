const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const elements = new Map();
function element(selector) {
    if (!elements.has(selector)) {
        elements.set(selector, {
            0: {},
            find: element,
            text(value) { this.content = value; return this; },
            prop(name, value) { this[name] = value; return this; },
            empty() { return this; },
            addClass() { return this; },
            html(value) { this.content = value; return this; },
            appendTo() { return this; },
            attr() { return this; },
        });
    }
    return elements.get(selector);
}
const frappe = {
    pages: { "common-dashboard": {} },
    format: String,
    datetime: { str_to_user: String },
    utils: {},
    Chart: class { destroy() {} },
};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, "common_dashboard.js"), "utf8"), {
    frappe,
    $: element,
    __: (text, values = []) => text.replace("{0}", values[0]),
});
const chart = new frappe.pages["common-dashboard"].SiteBudgetChart(element("body"));
const sites = [
    { site: "Above", estimated_budget: 100, total_expenses: 125 },
    { site: "Equal", estimated_budget: 100, total_expenses: 100 },
    { site: "Below", estimated_budget: 100, total_expenses: 99 },
    { site: "Missing", estimated_budget: null, total_expenses: 101 },
    { site: "Zero budget", estimated_budget: 0, total_expenses: 1 },
];
chart.render({ sites, totals: {} });
const styles = element(".site-budget-bar-colors");
const definitions = element(".site-budget-color-definitions");
const notice = element(".site-budget-over-budget");
assert(styles.content.includes('.dataset-1 .bar[data-point-index="0"]'));
assert(styles.content.includes('.dataset-1 .bar[data-point-index="4"]'));
for (const index of [1, 2, 3]) {
    assert(!styles.content.includes(`data-point-index="${index}"`));
}
assert(!styles.content.includes(".dataset-0"), "Budget bars must retain their original color");
assert(styles.content.includes('fill: url("#site-budget-expense-0")'));
assert(definitions.content.includes('x1="0" y1="1" x2="0" y2="0"'), "Fill runs from bottom to top");
assert(definitions.content.includes('<stop offset="80%" stop-color="#FBBF24" />'),
    "The first 100 of 125 in expenses must stay amber");
assert(definitions.content.includes('<stop offset="80%" stop-color="#B22222" />'),
    "Only the remaining 25 of 125 in expenses must be red, with a sharp boundary");
assert(definitions.content.includes('<stop offset="0%" stop-color="#B22222" />'),
    "With a zero budget, all positive expenses exceed the budget");
assert.equal(notice.hidden, false);
assert(notice.content.includes("Above, Zero budget"));

chart.render({ sites: [sites[2], sites[0]], totals: {} });
assert(!styles.content.includes('data-point-index="0"'), "Refresh must discard old site positions");
assert(styles.content.includes('data-point-index="1"'));

chart.render({ sites: [{ ...sites[0], total_expenses: 90 }], totals: {} });
assert.equal(styles.content, "", "An expense reduced below budget must return to amber");
assert.equal(definitions.content, "", "Refresh must remove obsolete gradients");
assert.equal(notice.hidden, true);
chart.render({ sites: [], totals: {} });
assert.equal(styles.content, "");
assert.equal(notice.hidden, true);
console.log("PASS: only excess portions are red, threshold boundaries, missing/zero budgets and refresh cleanup.");
