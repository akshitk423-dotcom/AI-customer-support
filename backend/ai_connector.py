from backend.schemas import ComplaintRequest, ComplaintResponse

# This is a STUB (fake placeholder) standing in for the AI teammate's code.
# Later, replace the body of this function with a real call to their model.
def analyze_complaint(request: ComplaintRequest) -> ComplaintResponse:
    text = request.complaint_text

    # --- FAKE LOGIC just so the backend works end-to-end for now ---
    fake_category = "Billing"
    fake_urgency = "Medium"
    fake_summary = text[:50] + ("..." if len(text) > 50 else "")
    fake_department = "Billing Support Team"
    fake_reply = (
        f"Dear {request.customer_name}, thank you for reaching out. "
        f"We understand your concern and our {fake_department} "
        f"will get back to you shortly."
    )

    # Package everything into our standard response shape.
    return ComplaintResponse(
        category=fake_category,
        urgency=fake_urgency,
        summary=fake_summary,
        department=fake_department,
        reply=fake_reply,
    )
