// JavaScript Function to Retrieve Applicant Information
function getApplicantInfo() {
    console.log("here wai")

    let assetValue = document.querySelector("input[name='asset_code']").value;
    console.log(assetValue)
    // if (isNaN(assetValue) || assetValue.toString().length !== 11) {
    //     alert("Please enter a valid 11-digit CID (numeric only).");
    //     return;
    // }
    frappe.call({
        method: "erpnext.www.check-status.index.get_asset_info", // Replace with the actual method path
        args: {
            asset_code: assetValue
        },
        callback: function (r) {
            if (!r.message) {
                alert("Error: Unable to retrieve applicant information.");
                return;
            }
            console.log(r.message)
            displayAssetInfo(r.message);
        }
    });
}

function displayAssetInfo(response) {
    var infoContainer = document.getElementById("asset-info");

    if (response && response.asset_info && response.asset_info.length > 0) {
        var asset = response.asset_info[0]; // Access the first applicant in the array

        var tableHTML = '<table class="table table-bordered table-striped table-condensed table-custom-width">' +
            '<colgroup><col style="width: 50%;"><col style="width: 50%;"></colgroup>' +
            '<thead><tr><th colspan="2" class="table-heading-one">Asset Information</th></tr></thead>' +
            '<tbody>' +
            '<tr><td class="table-heading">Asset Code</td><td>' + asset.name + '</td></tr>' +
            '<tr><td class="table-heading">Asset Name</td><td>' + asset.asset_name + '</td></tr>' +
            '<tr><td class="table-heading">Custodian</td><td>' + asset.custodian + '</td></tr>' +
            '<tr><td class="table-heading">Branch/Cost Center</td><td>' + asset.branch + '</td></tr>' +
            '<tr><td class="table-heading">Purchase Date</td><td>' + asset.purchase_date + '</td></tr>' +
            '<tr><td class="table-heading">Asset Rate</td><td>' + asset.asset_rate + '</td></tr>' +
            '</tbody></table>';

        infoContainer.innerHTML = tableHTML;
    } else {
        infoContainer.innerHTML = '<p>No Record found</p>';
    }
}

frappe.ready(function () {
    console.log("loaded")
    // Get the input field
    let inputField = document.querySelector("input[name='asset_code']");
    let asset_code = inputField.value;

    // If input has a value, fetch and display details
    if (asset_code && asset_code.trim() !== "") {
        getApplicantInfo(asset_code);
    }
});