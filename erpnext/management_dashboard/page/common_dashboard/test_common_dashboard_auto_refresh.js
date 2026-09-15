const assert = require("assert");
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const timers = new Map();
const listeners = new Map();
let next_timer = 0;
const document = {
    hidden: false,
    addEventListener: (event, handler) => listeners.set(event, handler),
    removeEventListener: event => listeners.delete(event),
};
const frappe = { pages: { "common-dashboard": {} } };
vm.runInNewContext(fs.readFileSync(path.join(__dirname, "common_dashboard.js"), "utf8"), {
    frappe,
    document,
    setInterval: (callback, delay) => {
        assert.equal(delay, 60000);
        timers.set(++next_timer, callback);
        return next_timer;
    },
    clearInterval: timer => timers.delete(timer),
});
const element = { find: () => element };
const chart = new frappe.pages["common-dashboard"].SiteBudgetChart(element);
let requests = 0;
chart.refresh = () => requests++;
chart.start_auto_refresh();
assert.equal(requests, 1, "Opening the dashboard must fetch fresh data");
assert.equal(timers.size, 1);
[...timers.values()][0]();
assert.equal(requests, 2, "Timer must refresh the amounts");
document.hidden = true;
[...timers.values()][0]();
assert.equal(requests, 2, "Hidden tabs must not keep querying the ledger");
document.hidden = false;
listeners.get("visibilitychange")();
assert.equal(requests, 3, "Returning to the browser tab must fetch fresh data");
chart.start_auto_refresh();
assert.equal(requests, 3, "Page load followed by page show must not fetch twice");
assert.equal(timers.size, 1, "Repeated page show events must not duplicate timers");
assert.equal(listeners.size, 1);
chart.stop_auto_refresh();
assert.equal(timers.size, 0, "Leaving the dashboard must stop the timer");
assert.equal(listeners.size, 0, "Leaving the dashboard must remove the tab listener");
chart.start_auto_refresh();
assert.equal(requests, 4, "Reopening the dashboard must immediately request current values");
chart.stop_auto_refresh();
console.log("PASS: immediate loading and reopening, minute updates, hidden-tab pause and timer cleanup.");
