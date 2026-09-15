const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const elements = new Map();
function element(selector) {
    if (!elements.has(selector)) {
        elements.set(selector, {
            0: { innerHTML: "" },
            find: element,
            text(value) { this.content = value; return this; },
            prop(name, value) { this[name] = value; return this; },
            empty() { this[0].innerHTML = ""; return this; },
        });
    }
    return elements.get(selector);
}
const frappe = {
    pages: { "common-dashboard": {} },
    utils: {
        escape_html: value => value.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"),
    },
};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, "common_dashboard.js"), "utf8"), {
    frappe,
    __: (text, values = []) => text.replace("{0}", values[0]),
});
const controller = new frappe.pages["common-dashboard"].SiteBudgetChart(element("body"));
const progress = [
    { project: "GI-Gyalpoizhing", physical_progress: 81.57, financial_progress: null },
    { project: "GI-Tareythang", physical_progress: 85.61, financial_progress: -5 },
    { project: "GI-Jamtsholing", physical_progress: 88.55, financial_progress: 116.35 },
    { project: "GI-Pemathang", physical_progress: 89.43, financial_progress: 1041.21 },
    { project: "GI-Khotokha <&>", physical_progress: null, financial_progress: 0 },
];
controller.render_progress(progress);
const chart_element = element(".site-progress-chart")[0];
const svg = chart_element.innerHTML;
assert(svg.includes('viewBox="0 0 1100 360"'), "Responsive chart must retain the same aspect ratio");
assert.equal((svg.match(/class="site-progress-grid"/g) || []).length, 11, "Scale must have 0–100% ticks every 10%");
for (let value = 0; value <= 100; value += 10) {
    assert(svg.includes(`class="site-progress-tick">${value.toFixed(2)}%</text>`));
    assert(svg.includes(`class="site-progress-tick">${value}%</text>`));
}
assert(!svg.includes('class="site-progress-tick">200%'), "Overflow must not expand the scale");
assert(svg.includes("Gyalsung Project"));
assert(svg.includes("Progress Percent"));
assert(svg.includes("GI-Khotokha &lt;&amp;&gt;"), "Project names must be escaped");
assert(!svg.includes("GI-Khotokha <&>"));
const groups = [...svg.matchAll(/<g class="site-progress-bar" data-series="([^"]+)" data-point-index="(\d+)">([\s\S]*?)<\/g>/g)];
assert.equal(groups.length, 10, "Each of the five projects must have two values");
const financial = index => groups.find(group => group[1] === "financial_progress" && Number(group[2]) === index)[3];
for (const [index, actual] of [[2, "116.35%"], [3, "1041.21%"]]) {
    const bar = financial(index);
    assert(bar.includes('y="52"') && bar.includes('height="250"'), "An over-budget bar must end at 100%");
    assert(bar.includes(`Financial Progress: ${actual}</title>`), "Tooltip must retain the actual percentage");
    assert(bar.includes(`class="site-progress-value">${actual}</text>`), "Label must retain the actual percentage");
    assert(bar.includes('class="site-progress-overflow"'), "Overflow must be visibly marked");
}
assert(!financial(0).includes("<rect"), "An unknown percentage must not draw a zero bar");
assert(financial(0).includes("N/A"));
assert(financial(1).includes("-5.00%"), "A negative percentage must retain its true label");
assert(financial(4).includes("0.00%"), "An actual zero must be distinct from missing data");
assert.equal(controller.progress_status.hidden, true);

controller.render_progress(progress.map(row => ({ ...row, physical_progress: 50, financial_progress: 75 })));
assert(!chart_element.innerHTML.includes("1041.21%"), "Refresh must remove old values");
controller.render_progress([]);
assert.equal(chart_element.innerHTML, "", "Empty data must clear the previous chart");
assert.equal(controller.progress_chart, null);
assert.equal(controller.progress_status.hidden, false);
console.log("PASS: fixed 0–100% axes, 10% ticks, true overflow values, missing data, escaping and refresh cleanup.");
