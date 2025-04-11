import json

def generate_key_value(data):
    # Extract required fields
    br_id = data.get("br_id") or data.get("ukId")
    subscriber_id = data["subscriber_id"].rstrip('/')
    type_ = data["type"]

    # Determine the prefix based on the type
    if type_ == "BPP":
        prefix = "app-backend:taxi-bap:registry:"
    elif type_ == "BAP":
        prefix = "dynamic-offer-driver-app:dynamic-offer-driver-app:registry:"
    else:
        raise ValueError(f"Unsupported type: {type_}")

    # Construct the key
    key = f"{prefix}{br_id}|{subscriber_id}"

    # Prepare value structure
    value_data = {
        "city": data["city"],
        "country": data["country"],
        "created": data["created"],
        "domain": data["domain"],
        "encr_public_key": data["encr_public_key"],
        "signing_public_key": data["signing_public_key"],
        "status": data["status"],
        "subscriber_id": data["subscriber_id"],
        "subscriber_url": data["subscriber_url"].rstrip('/'),
        "type": data["type"],
        "ukId": data["ukId"],
        "updated": data["updated"],
        "valid_from": data["valid_from"],
        "valid_until": data["valid_until"]
    }

    # Convert to escaped JSON string
    value_json_str = json.dumps(value_data)
    escaped_value = json.dumps(value_json_str)

    return key, escaped_value

# Example usage
data = {
    "subscriber_id": "backend.choosecabs.com",
    "status": "SUBSCRIBED",
    "ukId": "66fe660998f25",
    "subscriber_url": "https://backend.choosecabs.com/api/trv10",
    "country": "IND",
    "domain": "ONDC:TRV10",
    "valid_from": "2024-12-11T13:44:54.101Z",
    "valid_until": "2030-06-19T11:57:54.101Z",
    "type": "BAP",
    "signing_public_key": "sgJgGe3xh8pdYoj5NrUuzKhx4h9P//UOY3jWtH5xz/M=",
    "encr_public_key": "MCowBQYDK2VuAyEAN683ZAgZUgv2n3xs8kLovdswU7Wbd39RrEVUBU0pZxE=",
    "created": "2024-12-11T11:26:52.374Z",
    "updated": "2024-12-11T11:26:52.381Z",
    "br_id": "66fe660998f25",
    "city": "std:022"
}

key, value = generate_key_value(data)
print("Key:\n", key)
print("\nValue:\n", value)
