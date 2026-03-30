CATEGORY_KEYWORDS = {
    "Food & Dining": [
        "grocery", "groceries", "restaurant", "pizza", "starbucks", "mcdonald",
        "burger", "sushi", "thai", "tavern", "fast food", "cafe", "diner",
        "chipotle", "subway", "doordash", "ubereats", "grubhub"
    ],
    "Entertainment": [
        "netflix", "spotify", "hulu", "disney", "cinema", "movies", "theater",
        "concert", "ticketmaster", "xbox", "playstation", "steam", "apple music"
    ],
    "Housing": [
        "mortgage", "rent", "lease", "hoa", "property tax"
    ],
    "Transport": [
        "shell", "exxon", "bp", "chevron", "gas station", "fuel", "uber",
        "lyft", "taxi", "parking", "toll", "transit", "metro", "bus"
    ],
    "Utilities": [
        "electric", "electricity", "water", "gas company", "internet", "wifi",
        "phone company", "mobile phone", "at&t", "verizon", "t-mobile", "comcast"
    ],
    "Shopping": [
        "amazon", "target", "walmart", "costco", "ebay", "etsy", "best buy",
        "hardware store", "home depot", "ikea", "zara", "h&m"
    ],
    "Health": [
        "pharmacy", "cvs", "walgreens", "doctor", "hospital", "clinic",
        "dentist", "gym", "fitness", "health"
    ],
    "Travel": [
        "airline", "flight", "hotel", "airbnb", "booking", "expedia",
        "marriott", "hilton", "delta", "united", "southwest"
    ],
    "Income": [
        "paycheck", "salary", "deposit", "direct deposit", "transfer in",
        "refund", "reimbursement"
    ],
}


def categorise(description: str) -> str:
    description_lower = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in description_lower:
                return category
    return "Other"
