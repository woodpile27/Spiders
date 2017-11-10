# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import logging
import requests



class ProxyMiddleware(object):

    logger = logging.getLogger(__name__)

    def process_request(self, request, spider):
        self.logger.debug('Using Proxy')
        request.meta['proxy'] = self.get_proxy()
        return None

    def process_response(self, request, response, spider):
        if response.status != 200:
            self.logger.debug('Changing Proxy')
            request.meta['proxy'] = self.get_proxy()
            request.dont_filter = True
            return request
        return response

    def get_proxy(self):
        try:
            url = 'http://127.0.0.1:5000/get'
            proxy = 'http://' + requests.get(url).text
            return proxy
        except Exception:
            self.get_proxy()
