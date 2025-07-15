import json

def parse_postman_json(json_file):
    data = json.load(json_file)
    results = data.get("results", [])
    parsed = []

    for item in results:
        name = item.get("name", "Unknown")
        times = item.get("times", [])
        parsed.append((name, times))

    return parsed
