# -*- coding: utf-8 -*-

import logging
import re
import urllib
import lxml.html

class Parser:

    _pattern_adsense_client = re.compile('google_ad_client=([\w\d-]+);')
    _pattern_adsense_slot = re.compile('google_ad_slot=([\d-]+);')
    _pattern_adsense_format = re.compile('google_ad_format=([\w\d-]+);')
    _pattern_cookie = re.compile('Set-Cookie: (id=[\d\w=|]+); expires')
    
    def cookieParse(self, headers):
        try:
            return self._pattern_cookie.search(headers).group(1)
        except AttributeError:
            return False

    def linkStatusSuccess(self, headers):
        return headers.find('HTTP/1.1 200 OK') >= 0

    def extractAdSense(self, source):

        if self.parseAdsenseFail(source):
            return None

        doc = lxml.html.document_fromstring(unicode(source,errors='ignore'))

        tmp = self.parseAdsense1(doc)
        if tmp:
            logging.debug('parse 1 type')
            return tmp

        tmp = self.parseAdsense2(doc)
        if tmp:
            logging.debug('parse 2 type')
            return tmp
        
        logging.debug('not parsed adsense')
        return False
        
    def parseAdsenseFail(self,source):
        return (
            source.strip() == '<html><body style="background-color:transparent"></body></html>'
            or
            len(source.strip()) == 0
          )

    def parseAdsense1(self,doc):
        adsense = []

        tables = doc.cssselect('#ads table.adc')      
        for table in tables:
            href = table.cssselect('a.adt')[0]
            adsense.append({ 'url': href.get('title'), 'title': href.text_content(), 'desc': table.cssselect('.adb')[0].text_content()})

        if len(tables) != len(adsense):
            logging.error('parse1 error')

        if len(adsense):
            return adsense
        else:
            return False



    def parseAdsense2(self,doc):
        div = doc.cssselect('#ads div.ad')
        if len(div) == 0:
            return False

        href = div[0].cssselect('a.adt')
        desc = div[0].cssselect('.adb')

        if len(href)!=1 or len(desc)!=1:
            logging.error('parse2 error')
            return False

        return [{ 'url': href[0].get('title'), 'title': href[0].text_content(), 'desc': desc[0].text_content()}]


    def parsePropLinks(self, url, source):
        source = re.sub('[\s\"\']', '', source)
        
        clients = [re.sub('^ca-', '', m.group(1)) for m in self._pattern_adsense_client.finditer(source)]
        slots = [{'value': m.group(1), 'position': m.start(), 'type':'slotname'} for m in self._pattern_adsense_slot.finditer(source)]
        formats = [{'value': m.group(1), 'position': m.start(), 'type':'format'} for m in self._pattern_adsense_format.finditer(source)]

        if len(clients) != (len(slots) + len(formats)):
            logging.error('%d clients, %d slots, %d formats' % (len(clients), len(slots), len(formats)))
            return []

        props = slots + formats
        props.sort(key=lambda x:x['position'])

        return [ "http://googleads.g.doubleclick.net/pagead/ads?%s" % urllib.urlencode({
                        'output':'html',
                        'client': 'ca-%s' % client,
                        'url': "http://%s/" % url,
                        'ad_type':'text',
                        props[i]['type']: props[i]['value']
                    }) for i, client in enumerate(clients) ]


