import collections
import logging

import requests

import config
from py_src import db, utils


class UnsupportedLanguage(AttributeError):

    def __init__(self, lang, param, meta_key):
        self.message = 'Unsupported language `{}` ' \
                       'for property parameter `{}` ' \
                       'and meta_key `{}`!'.format(lang, param, meta_key)
        super().__init__(self.message)


class Extractor:
    name = None
    meta_key = None

    @classmethod
    def get(cls, payload):
        raise NotImplementedError

    @classmethod
    def translate(cls, data, lang='en', vocabulary=None):
        return data

    @staticmethod
    def get_translated(original_text, vocabulary_variants):
        for variant in vocabulary_variants:
            if original_text == variant['name']:
                return variant['value']
        return original_text

    @staticmethod
    def get_meta_value(data):
        raise NotImplementedError

    @classmethod
    def update_post_meta(cls, meta_value, post_id):
        return db.add_post_meta(post_id, cls.meta_key, meta_value)


class DescriptionExtractor(Extractor):
    name = 'description'
    meta_keys = (
        'sections_1_content',
        'header_slideshow_{}_title'
    )

    @classmethod
    def get(cls, payload):
        result = payload.get('translatedDescriptions', {'translated': []})
        result['translated'].extend(payload.get('description', []))
        return result

    @classmethod
    def translate(cls, data, lang='en', vocabulary=None):
        base_template = data['translated'][0]

        for description in data['translated']:
            if description['code'] == lang.upper():
                return description
            if description['code'] in ('en', 'EN'):
                base_template = description

        return base_template

    @staticmethod
    def get_meta_value(data):
        return (
            data['headline'],
            '<h1>{headline}</h1>\n\n<br>'
            '<strong>{title}</strong>\n\n<br>\n\n<br>'
            '{description}'.format(
                headline=data['headline'],
                title=data.get('summary', '').replace('\n- ', '\n\n<br>\n- '),
                description=data['description'].replace('\n', '\n\n<br>\n')
            )
        )

    @classmethod
    def update_post_meta(cls, meta_values, post_id):
        results = []

        description_meta_key, slider_template_meta_key = cls.meta_keys
        slider_headline, description = meta_values

        results.append(db.add_post_meta(post_id, description_meta_key, description))

        for image_number in range(2):
            results.append(db.add_post_meta(
                post_id,
                slider_template_meta_key.format(image_number),
                slider_headline
            ))

        return results


class BedroomsExtractor(Extractor):
    name = 'rooms'
    meta_key = 'sections_3_boxes_list_0_box_sub_heading'

    @classmethod
    def get(cls, payload):
        result = []
        counter = collections.defaultdict(int)

        for room in payload['rooms'].get('bedrooms', {}).get('rooms', []):
            if not room:
                continue
            beds = room['beds']
            beds = beds[0] if beds else {}
            counter[room['type']] += 1
            result.append({
                'type': room.get('type') or room['name'],
                'name': beds.get('name'),
                'number': beds.get('number'),
                'index': counter[room['type']]
            })

        return result

    @classmethod
    def translate(cls, data, lang='en', vocabulary=None):
        for room in data:
            room['name'] = cls.get_translated(
                room['name'],
                vocabulary['Beds']['Bedroom beds']
            )
            if lang == 'de' and room['type'] == 'Bedroom':
                room['type'] = 'Schlafzimmer'
        return data

    @staticmethod
    def get_meta_value(data):
        texts = ['']

        for room in data:
            texts.append('{} {}:\n\n<br>{} {}'.format(
                room['type'],
                room['index'],
                room['number'],
                room['name'].lower()
            ))

        return '\n\n<br>\n\n<br>'.join(texts)


class AmenitiesExtractor(Extractor):
    name = 'amenities'
    meta_key = 'sections_3_boxes_list_1_box_sub_heading'

    @classmethod
    def get(cls, payload):
        result = {}

        facilities = payload['facilities']

        for amenity in config.AMENITIES.keys():
            availability = False
            value = facilities[amenity]
            if value is not None:
                availability = not value.startswith('No ')
            result[amenity] = {
                'description': value,
                'availability': availability
            }

        return result

    @classmethod
    def translate(cls, data, lang='en', vocabulary=None):
        for amenity_key, amenity_value in data.items():
            amenity_value['name'] = vocabulary['html'][amenity_key]
            amenity_value['description'] = cls.get_translated(
                amenity_value['description'],
                vocabulary['Facilities'][config.AMENITIES[amenity_key]]
            )
            amenity_value['translated_no'] = 'Keine' if lang == 'de' else 'No'
        return data

    @staticmethod
    def get_meta_value(data):
        texts = ['']

        for key, value in data.items():
            style = ''
            text = value['name']

            if not value['availability']:
                style = 'style="color: #999999;opacity: 0.5;"'
                text = '{} {}'.format(value['translated_no'], value['name'])

            text = '<span {}>{}</span>'.format(style, text)
            texts.append(text)

        return '\n\n<br>'.join(texts)


class KitchenExtractor(Extractor):
    name = 'kitchen'
    meta_key = 'sections_3_boxes_list_2_box_sub_heading'

    @classmethod
    def get(cls, payload):
        return payload['facilities']['kitchen']

    @classmethod
    def translate(cls, data, lang='en', vocabulary=None):
        result = []

        for kitchen_part in data:
            result.append(cls.get_translated(
                kitchen_part,
                vocabulary['Facilities']['Kitchen']
            ))

        return result

    @staticmethod
    def get_meta_value(data):
        return '\n\n<br>'.join(['', *data])


class LivingDiningExtractor(Extractor):
    name = 'livingDining'
    meta_key = 'sections_3_boxes_list_3_box_sub_heading'

    @classmethod
    def get(cls, payload):
        return payload['facilities']['livingDining']

    @classmethod
    def translate(cls, data, lang='en', vocabulary=None):
        result = []

        for ld_part in data:
            result.append(cls.get_translated(
                ld_part,
                vocabulary['Facilities']['Living Dining']
            ))

        return result

    @staticmethod
    def get_meta_value(data):
        return '\n\n<br>'.join(['', *data])


class OutdoorExtractor(Extractor):
    name = 'outdoor'
    meta_key = 'sections_3_boxes_list_4_box_sub_heading'

    @classmethod
    def get(cls, payload):
        return payload['facilities']['outdoor']

    @classmethod
    def translate(cls, data, lang='en', vocabulary=None):
        result = []

        for outdoor_part in data:
            result.append(cls.get_translated(
                outdoor_part,
                vocabulary['Facilities']['Outdoor']
            ))

        return result

    @staticmethod
    def get_meta_value(data):
        return '\n\n<br>'.join(['', *data])


class MiscellaneousExtractor(Extractor):
    name = 'miscellaneous'
    meta_key = 'sections_3_boxes_list_5_box_sub_heading'

    @classmethod
    def get(cls, payload):
        return payload['facilities']['miscellaneous']

    @classmethod
    def translate(cls, data, lang='en', vocabulary=None):
        result = []

        for miscellanea in data:
            result.append(cls.get_translated(
                miscellanea,
                vocabulary['Facilities']['Miscellaneous']
            ))

        return result

    @staticmethod
    def get_meta_value(data):
        return '\n\n<br>'.join(['', *data])


class DetailsExtractor(Extractor):
    name = 'details'
    meta_key = 'sections_5_features_list_0_feature_sub_heading'

    @classmethod
    def get(cls, payload):
        extras_and_services = None
        if 'extrasAndServices' in payload:
            extras_and_services = {'title': 'feesAndExtras', 'data': payload['extrasAndServices']}
            if 'cleaning' in extras_and_services['data']:
                extras_and_services['data']['cleaning']['name'] = 'Cleaning'

        suitability = {}
        for key, value in payload.get('suitability', {}).items():
            need_to_add = (
                key not in config.SUITABILITY_UNUSED_KEYS
                and not isinstance(value, (int, float, bool))
                and bool(value)
            )
            if need_to_add:
                suitability[key] = value

        return {
            'facts': {'title': 'Facts', 'data': cls._get_facts_data(payload)},
            'extras_and_services': extras_and_services,
            'rules': {
                'title': 'houseRules',
                'suitability': suitability,
                # `booking_rules` removed at the request of the client
                # 'booking_rules': payload['bookingRules'],
            }
        }

    @classmethod
    def _get_facts_data(cls, payload):
        rooms = payload['rooms']
        bedrooms = rooms.get('bedrooms', {})

        beds = []
        for room in bedrooms.get('rooms', []):
            if not room:
                continue
            for bed in room['beds']:
                beds.append(bed['number'])

        return {
            'rentalType': {'type': 'Type', 'name': payload['rentalType']},
            'floorspace': payload['floorspace'],
            'guest': {'number': payload['basicRates'].get('maximumGuests', 0)},
            'bedrooms': {'number': bedrooms.get('numbers', 0)},
            'beds': {'number': max([0, *beds])},
            'bathrooms': {'number': rooms.get('bathrooms', {}).get('numbers', 0)},
        }

    @classmethod
    def translate(cls, data, lang='en', vocabulary=None):
        data['facts'] = cls._translate_facts(data['facts'], vocabulary, lang)

        extras_and_services = data['extras_and_services']
        if extras_and_services:
            data['extras_and_services'] = cls._translate_extras_and_services(extras_and_services, vocabulary)

        house_rules_title = data['rules']['title']
        data['rules']['title'] = vocabulary['html'][house_rules_title]
        suitability = data['rules']['suitability']
        data['rules']['suitability'] = cls._translate_suitability(suitability, vocabulary)
        # `booking_rules` removed at the request of the client
        # booking_rules = data['rules']['booking_rules']
        # data['rules']['booking_rules'] = cls._translate_booking_rules(booking_rules, vocabulary)

        return data

    @classmethod
    def _translate_facts(cls, facts, vocabulary, lang):
        html_vocabulary = vocabulary['html']
        facts_data = facts['data']

        if lang == 'de':
            facts_data['rentalType']['type'] = 'Immobilie'
        facts_data['floorspace']['name'] = html_vocabulary['space']
        facts_data['guest']['name'] = html_vocabulary['guests']
        facts_data['bathrooms']['name'] = html_vocabulary['bathroom']

        js_vocabulary = vocabulary['js']
        facts_data['guest']['maximum'] = js_vocabulary['maximum']
        facts_data['bedrooms']['name'] = js_vocabulary['bedrooms']
        facts_data['beds']['name'] = js_vocabulary['beds']

        return facts

    @classmethod
    def _translate_extras_and_services(cls, extras_and_services, vocabulary):
        title = extras_and_services['title']
        extras_and_services['title'] = vocabulary['html'][title]

        if 'cleaning' in extras_and_services['data']:
            cleaning = extras_and_services['data']['cleaning']
            cleaning['name'] = vocabulary['js'][cleaning['name']]
            cleaning['feeBasis'] = vocabulary['js'][cleaning['feeBasis']]

        optional_extras_basis = vocabulary['Extras']['OptionalExtrasBasis']
        optional_extras_names = vocabulary['Extras']['OptionalExtras']

        for extra in extras_and_services['data'].get('extras', []):
            name = extra['name']
            fee_basis = extra.get('feeBasis')

            extra['name'] = cls.get_translated(name, optional_extras_names)

            if fee_basis:
                fee_basis = cls.get_translated(fee_basis, optional_extras_basis)
                extra['feeBasis'] = fee_basis

        extras_and_services['free'] = vocabulary['html']['free']

        return extras_and_services

    @classmethod
    def _translate_suitability(cls, suitability, vocabulary):
        for data_key, vocabulary_key in config.SUITABILITY.items():
            if data_key in suitability:
                suitability[data_key] = cls.get_translated(
                    suitability[data_key],
                    vocabulary['House rules'][vocabulary_key]
                )

                if data_key == 'eventsOrParties':
                    suitability[data_key] = '{} {}'.format(
                        suitability[data_key],
                        vocabulary['html'][data_key]
                    )

        return suitability

    @classmethod
    def _translate_booking_rules(cls, booking_rules, vocabulary):
        booking_rules['advanceNotice'] = cls.get_translated(
            booking_rules['advanceNotice'],
            vocabulary['Booking rules']['Advance Notice']
        )
        return booking_rules

    @classmethod
    def get_meta_value(cls, data):
        texts = list()

        texts.append(cls._get_facts_meta_value(data['facts']))
        if data['extras_and_services']:
            texts.append(cls._get_extras_and_services_meta_value(data['extras_and_services']))
        texts.append(cls._get_rules_meta_value(data['rules']))

        return '\n\n<br>\n\n<br>'.join(texts)

    @staticmethod
    def _get_facts_meta_value(facts):
        facts_data = facts['data']

        guest = facts_data['guest']
        space = facts_data['floorspace']
        rental = facts_data['rentalType']

        texts = [
            '',
            '{}: {}'.format(rental['type'], rental['name'])
        ]
        if space:
            texts.append('{}: {}{}'.format(
                space['name'],
                space.get('amount', 0),
                space.get('units', '').replace('2', '²'))
            )
        if guest:
            texts.append('{number} {} ({}: {number})'.format(
                guest['name'],
                guest['maximum'],
                number=guest['number'])
            )

        for key in ('bedrooms', 'beds', 'bathrooms'):
            value = facts_data[key]
            texts.append('{} {}'.format(value['number'], value['name']))

        return '\n\n<br>'.join(texts)

    @staticmethod
    def _get_extras_and_services_meta_value(extras_and_services):
        def get_extra_text(extra, is_cleaning=False):
            if 'fee' not in extra:
                return '{}: {}'.format(extra['name'], extra['feeBasis'])

            if extra['fee'] == 0:
                return '{}: <b>{}</b>'.format(extra['name'], extras_and_services['free'])

            template = '{}: {} € ({})' if is_cleaning else '{}: <b>{} € {}</b>'
            return template.format(
                extra['name'],
                extra['fee'],
                extra['feeBasis'] if 'feeBasis' in extra else ''
            )

        texts = ['<strong>{}</strong>\n\n<br>'.format(extras_and_services['title'])]

        if 'taxes' in extras_and_services['data']:
            extras_and_services['data'].pop('taxes')

        if 'cleaning' in extras_and_services['data']:
            texts.append(get_extra_text(extras_and_services['data']['cleaning'], True))
        texts.extend(get_extra_text(extra) for extra in extras_and_services['data'].get('extras', []))

        if len(texts) == 1:
            texts.append('Keine')

        return '\n\n<br>'.join(texts)

    @staticmethod
    def _get_rules_meta_value(rules):
        texts = []
        house_rules = list(rules['suitability'].values())
        # `booking_rules` removed at the request of the client
        # house_rules.append(rules['booking_rules']['advanceNotice'])
        texts.append(
            '<strong>{}</strong>\n\n<br>\n\n<br>{}'.format(rules['title'], '\n\n<br>'.join(map(str, house_rules))))

        return '\n\n<br>\n\n<br>'.join(texts)


class ScriptAdder:
    name = None
    meta_key = None

    @classmethod
    def get(cls, property_number, lang, payload):
        raise NotImplementedError

    @classmethod
    def update_post_meta(cls, meta_value, post_id):
        return db.add_post_meta(post_id, cls.meta_key, meta_value)


class BookingScriptAdder(ScriptAdder):
    name = 'booking_script'
    meta_key = 'sections_5_features_list_0_feature_description'

    @classmethod
    def get(cls, property_number, lang, payload):
        script = r'''<script>(function(d, s, id) {
if (d.getElementById(id)) return;
var js, fjs = d.getElementsByTagName(s)[0];
js = d.createElement(s); js.id = id;
js.src = 'https://app.your.rentals/public/assets/scripts/direct-booking-widget.js';
fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'yr-direct-booking-widget-bootstrap'));</script>
<div class="yr-widget-direct-booking" data-yrscid="AUTE" data-yrlang="''' + lang + '''" data-yrlid="''' + str(
            property_number) + '''" data-yrtheme="z1ahkgnjt5"></div>'''

        return script


class MapScriptAdder(ScriptAdder):
    name = 'map_script'
    meta_key = 'sections_4_menu_group_0_menu_item_0_menu_item_heading'

    @classmethod
    def get(cls, property_number, lang, payload):
        location = payload['location']
        latitude, longitude = (
            str(location.get(key))
            for key in ('latitude', 'longitude')
        )
        script = r'''<style>
  #map{
    <br>height: 400px;
    <br>width: 100%;
  <br>}
<br></style>
<div id="map"></div>
<script>
  function initMap() {
    var uluru = {lat: ''' + latitude + ''', lng: ''' + longitude + '''};
    var map = new google.maps.Map(document.getElementById('map'), {
      zoom: 11,
      center: uluru
    });
    var marker = new google.maps.Marker({
      position: uluru,
      map: map
    });
  }
</script>
<script async defer 
    src="https://maps.googleapis.com/maps/api/js?key=''' + config.GOOGLE_MAP_API_KEY + '''&callback=initMap">
</script>'''

        return script


class ImagesExtractor:
    name = 'images'
    meta_key_templates = [
        'header_slideshow_{}_image',
        'sections_2_gallery_images_{}_gallery_image'
    ]

    @classmethod
    def get(cls, payload):
        results = []

        for img in payload['images']:
            extension = img['filename'].split('.')[-1].lower()
            path = img['src']
            img_url = '{}/{}.{}'.format(config.IMAGES_BASE_URL, path, extension)
            results.append(img_url)

        return results

    @classmethod
    def upload_images(cls, post_id, images_urls):
        images_ids = cls._wp_rest_post_images(images_urls)
        results = cls._update_posts_meta(post_id, images_ids)

        return results

    @classmethod
    def _wp_rest_post_images(cls, images_urls):
        images_ids = []

        session = requests.Session()
        session.auth = (config.WP_APPLICATION_PASSWORDS_USERNAME, config.WP_APPLICATION_PASSWORDS_PASSWORD)

        for img_url in images_urls:
            try:
                images_ids.append(cls._wp_post_or_return_image(img_url, session))
            except PermissionError:
                logging.warning('Unable upload image (server access denied)!')

        return images_ids

    @staticmethod
    def _wp_post_or_return_image(image_url, session):
        img_filename, img_name, image_extension = utils.get_image_name_and_extension(image_url)
        logging.info('Start extract image: {}'.format(image_url))

        wp_image = utils.get_wp_image(img_name)

        if wp_image:
            wp_img_id = wp_image['id']
            logging.info('Image {} already in WP (post_id = {})'.format(img_filename, wp_img_id))
            return wp_img_id

        headers = {
            'Content-Type': 'image/{}'.format(img_filename.lower()),
            'Content-Disposition': 'attachment; filename={}'.format(img_filename),
        }
        response = session.post(
            url=config.WP_REST_MEDIA_BASE_URL,
            headers=headers,
            data=utils.get_image(image_url)
        )

        if not (200 <= response.status_code < 300):
            raise PermissionError

        wp_img_id = response.json()['id']
        logging.info('Image {} inserted in WP (post_id = {})'.format(img_filename, wp_img_id))

        return wp_img_id

    @classmethod
    def _update_posts_meta(cls, post_id, images_ids):
        results = {}

        for index, img_id in enumerate(images_ids):
            meta_value = str(img_id)
            upd_result = cls._update_post_meta_image(post_id, index, meta_value)
            results[img_id] = upd_result

        return results

    @classmethod
    def _update_post_meta_image(cls, post_id, index, meta_value):
        res = []

        for template in cls.meta_key_templates:
            res.append(db.add_post_meta(post_id, template.format(index), meta_value))

        return res
