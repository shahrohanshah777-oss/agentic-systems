import json
import sys
from typing import Any, Dict, List

import requests

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
REQUEST_TIMEOUT_SECONDS = 15
HTTP_OK = 200

DELIVERY_CITIES = [
    {"city": "Delhi", "latitude": 28.6139, "longitude": 77.2090},
    {"city": "Mumbai", "latitude": 19.0760, "longitude": 72.8777},
    {"city": "Bengaluru", "latitude": 12.9716, "longitude": 77.5946},
]


def demo_json_round_trip() -> None:
    json_response_string = """
    {
        "order_id": "ORD-88421",
        "status": "out_for_delivery",
        "customer_city": "Delhi",
        "eta_hours": 4
    }
    """

    order = json.loads(json_response_string)

    print("STAGE 1 — json.loads(): parsed a JSON string into a Python dict")
    print("  Order ID :", order["order_id"])
    print("  Status   :", order["status"])
    print("  City     :", order["customer_city"])
    print("  Parsed type:", type(order))

    tracking_update = {
        "order_id": "ORD-88421",
        "event": "courier_picked_up",
        "city": "Delhi",
    }
    json_to_send = json.dumps(tracking_update, indent=2)

    print("\n  json.dumps(): Python dict -> JSON text ready to send/log")
    print(json_to_send)
    print("  Serialized type:", type(json_to_send))


def fetch_current_weather(latitude: float, longitude: float) -> Dict[str, Any]:
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": "temperature_2m,weather_code",
    }

    response = requests.get(OPEN_METEO_URL, params=params, timeout=REQUEST_TIMEOUT_SECONDS)

    print(f"  Weather API status code: {response.status_code}")

    if response.status_code != HTTP_OK:
        print("  Weather API call failed. Body preview (first 500 chars):")
        print(response.text[:500])
        sys.exit(1)

    return response.json()


def extract_weather_fields(city_name: str, weather_data: Dict[str, Any]) -> Dict[str, Any]:
    current = weather_data["current"]
    return {
        "city": city_name,
        "temperature_c": current["temperature_2m"],
        "weather_code": current["weather_code"],
        "latitude": weather_data["latitude"],
        "longitude": weather_data["longitude"],
    }


def report_city_weather(city_record: Dict[str, Any]) -> Dict[str, Any]:
    city = city_record["city"]
    print("\n" + "=" * 72)
    print(f"Delivery city: {city}")
    print("=" * 72)

    weather_data = fetch_current_weather(city_record["latitude"], city_record["longitude"])

    fields = extract_weather_fields(city, weather_data)

    print("  Extracted fields (this dict feeds agent tools in the next session):")
    print(json.dumps(fields, indent=2))

    print("  temperature_c type:", type(fields["temperature_c"]))

    return fields


def main() -> None:
    demo_json_round_trip()

    print("\n\n" + "#" * 72)
    print("LIVE WEATHER GET FOR EACH DELIVERY CITY")
    print("#" * 72)

    all_fields: List[Dict[str, Any]] = []
    for city_record in DELIVERY_CITIES:
        all_fields.append(report_city_weather(city_record))

    print("\n\n" + "#" * 72)
    print("SUMMARY — live temperature per delivery city")
    print("#" * 72)
    for fields in all_fields:
        print(f"  {fields['city']:<12} {fields['temperature_c']}°C  (weather_code={fields['weather_code']})")

    print("\nLab complete — structured weather data ready for agent tools (next session).")


if __name__ == "__main__":
    main()