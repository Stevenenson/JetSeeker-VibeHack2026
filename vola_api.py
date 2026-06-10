import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

# Vola.ro API configuration
VOLA_API_KEY = os.getenv('VOLA_API_KEY')
VOLA_API_BASE = 'https://www.vola.ro/api/v1'


def search_flights_real(origin_code: str, dest_code: str, departure_date: str, return_date: str) -> dict:
    """
    Search for real flight prices using Vola.ro's API.
    
    Args:
        origin_code: IATA city code of departure (e.g., 'BUH' for Bucharest)
        dest_code: IATA city code of destination (e.g., 'PAR' for Paris)
        departure_date: Departure date in 'YYYY-MM-DD' format
        return_date: Return date in 'YYYY-MM-DD' format
    
    Returns:
        dict with flight results or error message
    """
    print(f"Searching flights: {origin_code} -> {dest_code} ({departure_date} / {return_date})")

    headers = {
        'accept': 'application/json',
        'accept-language': 'ro',
        'api-key': VOLA_API_KEY,
        'content-type': 'application/json',
        'origin': 'https://www.vola.ro',
        'referer': 'https://www.vola.ro/',
        'user-agent': (
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36'
        ),
        'x-affiliate': 'vola',
        'x-app-origin': 'new-front-end',
    }

    payload = {
        'dates': {
            'departureFrom': departure_date,
            'departureTo': departure_date,
            'returnFrom': return_date,
            'returnTo': return_date
        },
        'passengers': {
            'adults': 1,
            'children': 0,
            'infants': 0
        },
        'routes': [
            {
                'origin': {'code': origin_code, 'type': 'city'},
                'destination': {'code': dest_code, 'type': 'city'}
            }
        ],
        'cabin': 'economy',
        'type': 'roundtrip'
    }

    try:
        # Initiate search
        response = requests.post(
            f'{VOLA_API_BASE}/flights/search',
            headers=headers,
            json=payload,
            timeout=15
        )
        response.raise_for_status()
        data = response.json()

        search_id = data.get('searchId')
        if not search_id:
            return {"error": "No search ID returned", "raw": data}

        # Poll for results (Vola uses async search)
        for attempt in range(10):
            time.sleep(2)
            result_response = requests.get(
                f'{VOLA_API_BASE}/flights/search/{search_id}/results',
                headers=headers,
                timeout=15
            )
            result_response.raise_for_status()
            results = result_response.json()

            flights = results.get('flights', [])
            if flights:
                # Format top 5 results
                formatted = []
                for flight in flights[:5]:
                    formatted.append({
                        'price': flight.get('price', {}).get('amount', 'N/A'),
                        'currency': flight.get('price', {}).get('currency', 'EUR'),
                        'airline': flight.get('airline', 'Unknown'),
                        'departure': flight.get('departure', ''),
                        'arrival': flight.get('arrival', ''),
                        'duration': flight.get('duration', ''),
                        'stops': flight.get('stops', 0)
                    })
                return {"flights": formatted, "total_found": len(flights)}

        return {"error": "Search timed out — no results found. Try different dates."}

    except requests.RequestException as e:
        print(f"[API ERROR] {e}")
        return {"error": f"Failed to fetch flights: {str(e)}"}
