// ===============================
// PAGE NAVIGATION
// ===============================

function showSection(sectionId) {

    const sections = document.querySelectorAll(".section");

    sections.forEach(section => {
        section.classList.remove("active-section");
    });

    document.getElementById(sectionId).classList.add("active-section");

    const buttons = document.querySelectorAll(".menu button");

    buttons.forEach(button => {
        button.classList.remove("active");
    });

    if (sectionId === "dashboard") {
        buttons[0].classList.add("active");
    }

    if (sectionId === "analyzer") {
        buttons[1].classList.add("active");
    }

    if (sectionId === "analytics") {
        buttons[2].classList.add("active");
    }
}


// ===============================
// COMPLAINT ANALYZER
// ===============================

function analyzeComplaint() {

    const complaint =
        document.getElementById("complaintInput").value
        .toLowerCase()
        .trim();

    if (complaint === "") {
        alert("Please enter a customer complaint first.");
        return;
    }


    let category = "General";
    let urgency = "Low";
    let department = "Support";
    let summary = "";
    let action = "";


    // DELIVERY

    if (
        complaint.includes("delivery") ||
        complaint.includes("delivered") ||
        complaint.includes("package") ||
        complaint.includes("parcel") ||
        complaint.includes("tracking") ||
        complaint.includes("arrive") ||
        complaint.includes("shipping")
    ) {

        category = "Delivery";
        department = "Logistics";

        if (
            complaint.includes("late") ||
            complaint.includes("delayed") ||
            complaint.includes("days") ||
            complaint.includes("not arrived")
        ) {
            urgency = "High";
        } else {
            urgency = "Medium";
        }

        summary = "Customer is facing an issue related to order delivery or shipment tracking.";

        action = "Check courier and shipment status and provide the customer with an updated delivery timeline.";
    }


    // PRODUCT

    else if (
        complaint.includes("broken") ||
        complaint.includes("damaged") ||
        complaint.includes("defective") ||
        complaint.includes("wrong product") ||
        complaint.includes("product")
    ) {

        category = "Product";
        department = "Support";

        if (
            complaint.includes("broken") ||
            complaint.includes("damaged") ||
            complaint.includes("defective")
        ) {
            urgency = "High";
        } else {
            urgency = "Medium";
        }

        summary = "Customer reported an issue with the received product.";

        action = "Verify the product issue and arrange replacement or technical support.";
    }


    // PAYMENT

    else if (
        complaint.includes("payment") ||
        complaint.includes("charged") ||
        complaint.includes("transaction") ||
        complaint.includes("money")
    ) {

        category = "Payment";
        department = "Finance";
        urgency = "High";

        summary = "Customer is facing a payment or transaction-related issue.";

        action = "Verify the transaction details and check whether the payment was successfully processed.";
    }


    // REFUND

    else if (
        complaint.includes("refund") ||
        complaint.includes("return") ||
        complaint.includes("money back")
    ) {

        category = "Refund";
        department = "Returns";
        urgency = "Medium";

        summary = "Customer wants to return the product or receive a refund.";

        action = "Check the order and refund eligibility, then initiate the return/refund process.";
    }


    // CANCELLATION

    else if (
        complaint.includes("cancel") ||
        complaint.includes("cancellation")
    ) {

        category = "Cancellation";
        department = "Support";
        urgency = "Medium";

        summary = "Customer wants to cancel an existing order.";

        action = "Verify the order status and check whether cancellation is still possible.";
    }


    // GENERAL

    else {

        category = "General";
        department = "Support";
        urgency = "Low";

        summary = "Customer has submitted a general support request.";

        action = "Review the customer's request and assign it to the appropriate support representative.";
    }


    // DISPLAY RESULTS

    document.getElementById("resultCategory").innerText = category;
    document.getElementById("resultUrgency").innerText = urgency;
    document.getElementById("resultDepartment").innerText = department;

    document.getElementById("resultSummary").innerText = summary;
    document.getElementById("resultAction").innerText = action;


    // GENERATE REPLY

    const reply =
        "Dear Customer,\n\n" +
        "Thank you for contacting us. We sincerely apologize for the inconvenience you are experiencing. " +
        "We have identified your issue as a " + category.toLowerCase() +
        " related concern and our " + department.toLowerCase() +
        " team will review it.\n\n" +
        action +
        "\n\nWe appreciate your patience and understanding.\n\n" +
        "Regards,\nCustomer Support Team";


    document.getElementById("generatedReply").innerText = reply;


    // UPDATE DASHBOARD COUNT

    let total =
        parseInt(document.getElementById("totalComplaints").innerText);

    total++;

    document.getElementById("totalComplaints").innerText = total;


    if (urgency === "High") {

        let high =
            parseInt(document.getElementById("highComplaints").innerText);

        high++;

        document.getElementById("highComplaints").innerText = high;
    }
}


// ===============================
// CLEAR COMPLAINT
// ===============================

function clearComplaint() {

    document.getElementById("complaintInput").value = "";

    document.getElementById("resultCategory").innerText = "—";
    document.getElementById("resultUrgency").innerText = "—";
    document.getElementById("resultDepartment").innerText = "—";

    document.getElementById("resultSummary").innerText =
        "Analysis will appear here.";

    document.getElementById("resultAction").innerText = "—";

    document.getElementById("generatedReply").innerText =
        "Your AI-generated response will appear here after analysis.";
}


// ===============================
// COPY GENERATED REPLY
// ===============================

function copyReply() {

    const reply =
        document.getElementById("generatedReply").innerText;

    navigator.clipboard.writeText(reply);

    alert("Reply copied successfully!");
}
