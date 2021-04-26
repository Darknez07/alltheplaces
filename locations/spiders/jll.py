# -*- coding: utf-8 -*-
import json
import re

import scrapy

from locations.items import GeojsonPointItem
from locations.hours import OpeningHours


class JllSpider(scrapy.Spider):
    name = "jll"
    allowed_domains = ["jll.com"]
    item_attributes = {'brand': 'JLL'}

    def start_requests(self):
        base_url = 'https://www.us.jll.com/bin/jll/search?q=locations&currentPage=/content/jll-dot-com/countries/amer/us/en/locations&top=100&p={page}&contentTypes=Location'
        pages = ["1", "2", "3", "4"]

        for page in pages:
            url = base_url.format(page=page)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        data = json.loads(response.body_as_unicode())

        for place in data["azureSearch"]["value"]:
            properties = {
                'ref': place["id"],
                'name': place["title"],
                'addr_full': place["streetAddress"],
                'city': place["city"],
                'state': place["stateProvince"],
                'postcode': place["postalCode"],
                'country': place["country"],
                'lat': place["latitude"],
                'lon': place["longitude"],
                'phone': place["telephoneNumber"],
                'website': place["cityPageLink"]
            }

            yield GeojsonPointItem(**properties)
