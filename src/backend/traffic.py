#To find coordinates of particular locations.

import requests

def get_road_coordinates(road_name, area="Bangalore"):
    # Bounding box for Bangalore: (south, west, north, east)
    bbox = "12.80,77.50,13.10,77.75"

    query = f"""
    [out:json];
    way["name"="{road_name}"]({bbox});
    out geom;
    """

    url = "https://overpass-api.de/api/interpreter"
    response = requests.get(url, params={"data": query})

    if response.status_code != 200:
        print(f"Error fetching data for {road_name}")
        return None

    data = response.json()

    if not data['elements']:
        print(f"No data found for {road_name}")
        return None

    # Get the geometry of the first matched road
    geometry = data['elements'][0]['geometry']
    start = geometry[0]
    end = geometry[-1]

    return {
        "road": road_name,
        "startlat": start['lat'],
        "startlong": start['lon'],
        "endlat": end['lat'],
        "endlong": end['lon']
    }

# Example usage
roads = [
    "MG Road",
    "Koramangala Road",
    "Electronic City Road",
    "Bannerghatta Road",
    "Outer Ring Road",
    "Hebbal Flyover",
    "Sarjapur Road",
    "Jayanagar 4th Block",
    "Bangalore Palace Road",
    "Church Street",
    "Vidhana Soudha Road",
    "Airport Road",
    "Kengeri Road",
    "Hosur Road",
    "Marathahalli Bridge",
    "Bellandur Road",
    "Old Airport Road",
    "Rajajinagar Main Road",
    "Banaswadi Road",
    "Cunningham Road",
    "Jeevan Bhima Nagar",
    "Vishweshwarapura",
    "Kasturinagar Main Road",
    "Nagasandra Road",
    "Basavanagudi Road",
    "Thippasandra Main Road",
    "Shivaji Nagar Road",
    "KR Puram Main Road",
    "Malleshwaram 8th Cross",
    "Bangalore-Mysore Road",
    "Rajmahal Vilas Road",
    "Shanthinagar Road",
    "Banaswadi Main Road",
    "Kanakapura Road",
    "Whitefield Main Road",
    "Ulsoor Lake Road",
    "Hennur Main Road",
    "Anand Rao Circle",
    "BTM Layout Main Road",
    "Yelahanka Road",
    "Chickpet Road",
    "Kempapura Main Road",
    "Sankey Road",
    "Indiranagar 100 Feet Road",
    "Commercial Street",
    "Koramangala 5th Block",
    "Chandapura Road",
    "Bangalore Outer Ring Road",
    "Vikram Sarabhai Road",
    "Rajajinagar 2nd Block",
    "Shivaji Nagar Market Road",
    "Malleswaram 15th Cross",
    "KR Road",
    "R T Nagar Main Road",
    "Yelahanka New Town Road",
    "Jakkur Road",
    "Magadi Road",
    "Bellary Road",
    "Chikka Adugodi Road",
    "Koramangala 4th Block",
    "Kengeri Main Road",
    "Kasturba Road",
    "Raja Rajeshwari Nagar Main Road",
    "Kumaraswamy Layout",
    "Bangalore University Road",
    "Kammanahalli Main Road",
    "Sadarahalli Road",
    "Magrath Road",
    "Vasanthnagar Road",
    "Benson Town Road",
    "Wilson Garden Road"
]




for road in roads:
    coords = get_road_coordinates(road)
    if coords:
        print(coords)
