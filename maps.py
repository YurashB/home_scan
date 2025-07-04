import os
from datetime import datetime, timedelta

import googlemaps
from dotenv import load_dotenv
from googlemaps.exceptions import ApiError

load_dotenv()

google_map_key = os.environ.get('GOOGLE_MAP_KEY')
gmaps = googlemaps.Client(key=google_map_key)
capgemini_address = "вулиця Сім'ї Прахових, 50, Київ, 020000"
betonenergo_address = "Бульвар Миколи Міхновського, 38, Київ, 01104"
home_address = 'Київ, ' + 'Янгеля 20'


def pick_street_url(points):
    return (f"https://maps.googleapis.com/maps/api/staticmap"
            f"?center={points['lat']},{points['lng']}"
            f"&zoom=12"
            f"&size=600x400"
            f"&markers=color:red%7C{points['lat']},{points['lng']}"
            f"&key={google_map_key}")



def get_street(title):
    try:
        return 'вул' + title.split('вул')[1]
    except Exception:
        return ''


def get_maps_info(street):
    arrival_time_v = datetime.now().replace(hour=9) + timedelta(days=1)
    mode = 'transit'
    units = 'metrics'
    try:
        from_home_to_cap = gmaps.directions(street, capgemini_address, mode, arrival_time=arrival_time_v)
        from_home_to_beton = gmaps.directions(street, betonenergo_address, mode, arrival_time=arrival_time_v)
        home_point = from_home_to_cap[0]["legs"][0]["start_location"]

        to_cap_dist = from_home_to_cap[0]['legs'][0]['distance']['text']
        to_cap_time = from_home_to_cap[0]['legs'][0]['duration']['text']

        to_beton_dist = from_home_to_beton[0]['legs'][0]['distance']['text']
        to_beton_time = from_home_to_beton[0]['legs'][0]['duration']['text']

        return to_cap_dist, to_cap_time, to_beton_dist, to_beton_time, pick_street_url(home_point)
    except ApiError as error:
        return Exception('Cant process street')
