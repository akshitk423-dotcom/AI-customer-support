from backend.schemas import ComplaintRequest, ComplaintResponse

def analyze_complaint(request: ComplaintRequest) -> ComplaintResponse:
    text = request.complaint_text
    lowered = text.lower()
    rules = [
        (("delivery", "delivered", "package", "parcel", "tracking", "arrive", "shipping", "late", "delayed"), "Delivery", "Logistics", "Check the courier status and provide an updated delivery timeline."),
        (("broken", "damaged", "defective", "wrong product", "product", "color"), "Product", "Product Support", "Verify the product issue and arrange a replacement or technical support."),
        (("payment", "charged", "transaction", "money", "billing"), "Billing", "Billing Support", "Review the transaction and confirm whether the charge was processed correctly."),
        (("refund", "return", "money back"), "Refund", "Returns & Refunds", "Check return eligibility and begin the refund process."),
        (("cancel", "cancellation"), "Account", "Account Support", "Verify the order status and confirm whether cancellation is still possible."),
    ]
    category, department, action = "Other", "General Support", "Review the request and assign it to the appropriate support representative."
    for keywords, possible_category, possible_department, possible_action in rules:
        if any(keyword in lowered for keyword in keywords):
            category, department, action = possible_category, possible_department, possible_action
            break
    urgency = "Critical" if any(word in lowered for word in ("fraud", "stolen", "unsafe", "urgent", "immediately")) else "High" if any(word in lowered for word in ("not arrived", "delayed", "broken", "damaged", "failed", "charged twice", "defective")) else "Medium" if category != "Other" else "Low"
    summary = text.strip()
    if len(summary) > 120:
        summary = summary[:117].rstrip() + "..."
    return ComplaintResponse(
        category=category,
        urgency=urgency,
        summary=summary,
        department=department,
        suggested_action=action,
        reply=f"Dear {request.customer_name},\n\nThank you for contacting us. We are sorry you are experiencing this issue. Our {department} team will review your request. {action}\n\nWe appreciate your patience.\n\nRegards,\nCustomer Support Team",
    )
