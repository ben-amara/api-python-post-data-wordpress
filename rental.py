import argparse
import logging

from py_src import utils
from py_src.orchestrator import Orchestrator


logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)


def parse_property(number, post_id, lang='en'):
    raw_property = utils.get_raw_property(number)
    logging.info('Gotten raw_property')
    vocabulary = utils.get_vocabulary(number, lang)
    logging.info('Gotten vocabulary')

    orchestrator = Orchestrator(number, raw_property, vocabulary, lang)

    result = orchestrator.parse(post_id)

    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("number", help="number of property", type=int, default=36325)
    parser.add_argument("post_id", help="post id", type=str, default=32)
    parser.add_argument("lang", help="language", type=str, default='de')
    args = parser.parse_args()

    payload_number, payload_post_id, payload_lang = args.number, args.post_id, args.lang

    parse_property(payload_number, payload_post_id, payload_lang)
