import json
import re

import requests

import config


IMAGE_SUFFIXES = ('', 'medium')

JS_FORCE_TRANSLATE = {
    'Cleaning': 'Endreinigung'
}


def get_raw_property(number):
    url = config.PAYLOAD_TEMPLATE_URL.format(number)
    response = requests.get(url)
    try:
        payload = response.json()
    except json.decoder.JSONDecodeError:
        raise PermissionError('Broken property data!')

    is_active = payload.get('active', True)
    is_published = (
            payload.get('published', False)
            or payload.get('wasPublished', False)
    )

    if response.status_code != 200 or not is_active or not is_published:
        raise PermissionError('Useless property!')

    return payload


def get_vocabulary(number, lang):
    url = config.RENTAL_VOCABULARY_TEMPLATE_URL.format(lang)
    headers = {'Origin': config.RENTAL_URL}
    response = requests.get(url, headers=headers)
    result = response.json()
    result.update({
        'js': _get_js_translations(number, lang),
        'html': _get_html_translations(lang)
    })
    return result


def _get_js_translations(number, lang):
    url = config.RENTAL_PAGE_TEMPLATE_URL.format(number, lang)
    response = requests.get(url)

    for line in response.content.decode('utf-8').split('\n'):
        founded = re.findall(r'\s+var translations = (.+);', line)
        if founded:
            result = json.loads(json.loads(founded[0]))
            result.update(JS_FORCE_TRANSLATE)
            return result


def _get_html_translations(lang):
    facts = (
        ('space', r'<span>(.+):\s+{{previewVm.floorspace.amount}}'),
        ('guests', r'maximumGuests}}\s+(.+)<span'),
        ('maximum', r'maximumAdditionalGuests}}\s+(.+)<\/span'),
        ('bathroom', r'numberOfBathrooms}}\s+(.+)<\/p>'),
        ('eventsOrParties', r'.eventsOrParties]}}\s+(.+)<\/li>'),

        ('houseRules', r'check"><\/span>(.+)<\/h2>'),
        ('additionalRules', r'<p><strong>(.+):<\/strong>'),
        ('feesAndExtras', r'dollar"><\/span>(.+)<\/h2>'),
        ('free', r'fee === 0" class="lower-case">&nbsp;(.+)<\/b><b'),
    )
    amenities = ('internet', 'parking', 'washingMachine', 'heating', 'airConditioning', 'swimmingPool')

    result = {}

    response = requests.get(config.RENTAL_PREVIEW_URL, cookies={'lang': lang})
    text = response.content.decode('utf-8')

    for key, regexp in facts:
        value = re.findall(regexp, text)
        result[key] = value[0] if value else None

    for key in amenities:
        regexp = key + r'\)}"\s+class="amen-tex">(.+)\s+<'
        value = re.findall(regexp, text)
        result[key] = value[0] if value else None

    return result


def get_image_name_and_extension(image_url):
    image_filename = image_url.split('/')[-1]
    image_name, image_extension = image_filename.split('.')
    return image_filename, image_name, image_extension


class BaseHTTPError(object):
    pass


def get_image(image_url):
    for suffix in IMAGE_SUFFIXES:
        if suffix:
            divided = image_url.split('.')
            image_url = '{}-{}.{}'.format('.'.join(divided[0:-1]), suffix, divided[-1])
        response = requests.get(image_url)
        if response.status_code == 200:
            return response.content


def get_wp_image(slug):
    url = config.WP_GET_MEDIA_TEMPLATE_URL.format(slug)
    rsp = requests.get(url)
    payload = rsp.json()
    if payload:
        return payload[0]
    return False
