# -*- coding: utf-8 -*-
import json
import re

import scrapy

from locations.items import GeojsonPointItem
from locations.hours import OpeningHours


class JacksonHewittSpider(scrapy.Spider):
    name = "jackson_hewitt"
    item_attributes = {'brand': "Jackson Hewitt"}
    allowed_domains = ['https://www.jacksonhewitt.com/']

    def start_requests(self):
        base_url = 'https://www.jacksonhewitt.com/api/offices/search?customerAddress%5Blatitude%5D={lat}&customerAddress%5Blongitude%5D={lon}'

        with open('./locations/searchable_points/us_centroids_25mile_radius.csv') as points:
            next(points)
            for point in points:
                _, lat, lon = point.strip().split(',')
                url = base_url.format(lat=lat, lon=lon)
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        xml = scrapy.selector.Selector(response)
        xml.remove_namespaces()

        places = xml.xpath('//OfficeLocation').extract()

        for place in places:
            properties = {
                'ref': re.search('<OfficeNumber>(.*)<\/OfficeNumber>', place).groups()[0],
                'addr_full': re.search('<Address1>(.*)<\/Address1>', place).groups()[0],
                'city': re.search('<City>(.*)<\/City>', place).groups()[0],
                'state': re.search('<State>(.*)<\/State>', place).groups()[0],
                'postcode': re.search('<ZipCode>(.*)<\/ZipCode>', place).groups()[0],
                'country': "US",
                'lat': re.search('<Latitude>(.*)<\/Latitude>', place).groups()[0],
                'lon': re.search('<Longitude>(.*)<\/Longitude>', place).groups()[0],
                'phone': re.search('<Phone>(.*)<\/Phone>', place).groups()[0],
                'extras':
                    {
                        'location_type': re.search('<Seasonal>(.*)<\/Seasonal>', place).groups()[0],
                        # Is this a permanent or seasonal location
                        'type_name': re.search('<TypeName>(.*)<\/TypeName>', place).groups()[0]
                        # Is this a storefront or walmart location
                    }
            }

            yield GeojsonPointItem(**properties)
