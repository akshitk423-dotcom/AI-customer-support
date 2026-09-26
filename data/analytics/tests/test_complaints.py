def test_ai_output(ai_output, expected):

    results = {}

    results["category"] = (
        ai_output["category"] == expected["category"]
    )

    results["urgency"] = (
        ai_output["urgency"] == expected["urgency"]
    )

    results["department"] = (
        ai_output["department"] == expected["department"]
    )

    return results


expected = {
    "category": "Delivery",
    "urgency": "High",
    "department": "Logistics"
}


ai_output = {
    "category": "Delivery",
    "urgency": "High",
    "department": "Logistics"
}


result = test_ai_output(ai_output, expected)


print("AI TEST RESULTS")
print("----------------")

for key, value in result.items():

    if value:
        print(key, ": PASS")
    else:
        print(key, ": FAIL")
