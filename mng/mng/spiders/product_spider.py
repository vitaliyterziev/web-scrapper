import scrapy
import re
import json


class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = [
        'https://shop.mango.com/bg-en/women/skirts-midi/midi-satin-skirt_17042020.html?c=99'
    ]

    def parse(self, response):
        for script in response.css('script::text').getall():
            if 'dataLayerV2Json' in script:
                self.product_id = re.findall(
                    '"id":"\d+"', script)[0].split(':')[1].replace('"', '')
                self.color_id = re.findall(
                    '"colorId":"\d+"', script)[0].split(':')[1].replace('"', '')

        url = 'https://shop.mango.com/services/stock-id'
        req = scrapy.Request(url,
                             method='GET',
                             headers={},
                             callback=self.parser2)
        yield req

    def parser2(self, response):
        res_dict = json.loads(response.body)
        url = f'https://shop.mango.com/services/garments/{self.product_id}'
        req = scrapy.Request(url,
                             method='GET',
                             headers={
                                 'stock-id': res_dict['key']},
                             callback=self.parser3)
        yield req

    def parser3(self, response):
        filename = 'product.json'
        product_dict = json.loads(response.body)

        name = product_dict['name']
        price = product_dict['price']['price']
        color, size = [(c['label'], c['sizes'][1:]) for c in product_dict['colors']['colors'] if c['id'] == self.color_id][0]

        with open(filename, 'w') as f:
            f.write(json.dumps({'name': name, 'price': price, 'color': color, 'size': size}, indent=4))
            self.log(f'Saved file {filename}')
