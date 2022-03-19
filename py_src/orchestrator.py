import logging

from py_src import extract


class Orchestrator:

    def __init__(self, property_number, raw_property, vocabulary, lang):
        self._property_number = property_number
        self._raw_property = raw_property
        self._vocabulary = vocabulary
        self._lang = lang

    def parse(self, post_id):
        extract_properties_results = self._extract_property_topics(post_id)
        add_script_result = self._add_scripts(post_id)
        extract_images_results = self._extract_images(post_id)

        return [
            extract_properties_results,
            add_script_result,
            extract_images_results
        ]

    def _extract_property_topics(self, post_id):
        results = []

        for extractor in self.__get_extractors():
            e_data = extractor.get(self._raw_property)
            translated = extractor.translate(e_data, self._lang, self._vocabulary)
            meta_value = extractor.get_meta_value(translated)
            results.append(extractor.update_post_meta(meta_value, post_id))
            logging.info('{}: parameter extracted'.format(extractor.__name__))

        logging.info('All topics extracted')

        return results

    @staticmethod
    def __get_extractors():
        return (
            extract.DescriptionExtractor,
            extract.BedroomsExtractor,
            extract.AmenitiesExtractor,
            extract.KitchenExtractor,
            extract.LivingDiningExtractor,
            extract.OutdoorExtractor,
            extract.MiscellaneousExtractor,
            extract.DetailsExtractor,
        )

    def _add_scripts(self, post_id):
        results = []

        for script_adder in self.__get_script_adders():
            meta_value = script_adder.get(self._property_number, self._lang, self._raw_property)
            results.append(script_adder.update_post_meta(meta_value, post_id))
            logging.info('{}: JS script added'.format(script_adder.__name__))

        return results

    @staticmethod
    def __get_script_adders():
        return (
            extract.BookingScriptAdder,
            extract.MapScriptAdder,
        )

    def _extract_images(self, post_id):
        img_extractor = extract.ImagesExtractor
        images_urls = img_extractor.get(self._raw_property)
        images_insert_results = img_extractor.upload_images(
            post_id, images_urls)

        logging.info('All images extracted')

        return images_insert_results
