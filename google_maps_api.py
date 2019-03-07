import random
import os
from googleplaces import GooglePlaces, types
google_places = GooglePlaces(os.environ.get('GOOGLE_MAPS_KEY'))
PLACES = []
# here is google maps api logic to randomly select a restaurant if the day is thursday or friday
takeout = google_places.nearby_search(
    location="38.968466, -94.609882",
    radius=20000, types=[types.TYPE_MEAL_TAKEAWAY])

restaurants = google_places.nearby_search(
    location="38.968466, -94.609882",
    radius=20000, types=[types.TYPE_RESTAURANT]
)

fast_food = google_places.nearby_search(
    location="38.968466, -94.609882", keyword="fast food",
    radius=20000, types=[types.TYPE_FOOD]
)

random_takeout = takeout.places
random_restaurant = restaurants.places
random_fast_food = fast_food.places

random.shuffle(random_takeout)
random.shuffle(random_restaurant)
random.shuffle(random_fast_food)

random_takeout[0].get_details()
random_restaurant[0].get_details()
random_fast_food[0].get_details()

PLACES.append({"name": random_takeout[0].name, "url": random_takeout[0].website, "rating": random_takeout[0].rating})
PLACES.append({"name": random_restaurant[0].name, "url": random_restaurant[0].website, "rating": random_restaurant[0].rating})
PLACES.append({"name": random_fast_food[0].name, "url": random_fast_food[0].website, "rating": random_fast_food[0].rating})

random.shuffle(PLACES)