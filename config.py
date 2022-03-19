from urllib.parse import urljoin

# MySQL
DB_TABLE_NAME = 'wp_42_postmeta'
DB_HOST = 'localhost'
DB_USERNAME = 'Ilya'
DB_PASSWORD = 'mRCGieYy6qLQMZVQ'
DB_NAME = 'autenticalnew_db'
# DB_TABLE_NAME = 'wp_postmeta'
# DB_HOST = 'localhost'
# DB_USERNAME = 'wordpress'
# DB_PASSWORD = 'wordpress'
# DB_NAME = 'wordpress'

# REST API CREDENTIALS
WP_APPLICATION_PASSWORDS_USERNAME = 'ilya'
WP_APPLICATION_PASSWORDS_PASSWORD = 'NiKs oqW9 7rSA dzzL 8pb6 mfe3'
# WP REST API
WP_REST_MEDIA_BASE_URL = 'https://autentical.de/wp-json/wp/v2/media'
WP_GET_MEDIA_TEMPLATE_URL = 'https://autentical.de/wp-json/wp/v2/media/?slug={}'

# Local testing wp rest api params
# WP_REST_MEDIA_BASE_URL = 'http://localhost:8000/?rest_route=/wp/v2/media'
# WP_GET_MEDIA_TEMPLATE_URL = 'http://localhost:8000/?rest_route=/wp/v2/media&slug={}'
# WP_APPLICATION_PASSWORDS_USERNAME = 'root'
# WP_APPLICATION_PASSWORDS_PASSWORD = 'pDg2 JaKV HCLZ HSdZ fOny sEbX'

# Google API
GOOGLE_MAP_API_KEY = 'AIzaSyAvMWHtumzEPugMMTKoxnFtU0AHrhGjQ-A'


# FURTHER - constants that do not require changes

# source urls
RENTAL_API_URL = 'https://api-internal.your.rentals'
PAYLOAD_TEMPLATE_URL = urljoin(RENTAL_API_URL, 'listing/guest/{}/AUTE')
RENTAL_VOCABULARY_TEMPLATE_URL = urljoin(RENTAL_API_URL, 'listing/values?lang={}')
RENTAL_URL = 'https://app.your.rentals'
RENTAL_PAGE_TEMPLATE_URL = urljoin(RENTAL_URL, 'book/property/{}?scid=AUTE&lang={}')
RENTAL_PREVIEW_URL = urljoin(RENTAL_URL, 'modules/preview/directives/views/yr-listing-preview.html')
IMAGES_BASE_URL = 'https://s3-eu-central-1.amazonaws.com/images.your.rentals'

# py_src keys
SUITABILITY = {
    'smoking': 'Smoking',
    'pets': 'Pets',
    'wheelchair': 'Wheelchair access',
    'eventsOrParties': 'Events or parties',
    'children': 'Children',
}
SUITABILITY_UNUSED_KEYS = {'petsCount', 'petFeeBasis', 'petsCount'}
AMENITIES = {
    'internet': 'Internet',
    'washingMachine': 'Washing machine',
    'airConditioning': 'Air-conditioning',
    'parking': 'Parking',
    'heating': 'Heating',
    'swimmingPool': 'Swimming pool'
}
