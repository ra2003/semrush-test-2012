#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time

import cStringIO
import pycurl
from parser import Parser
from db_operations import DB
from collections import Counter, deque

class Callbacks:

    db = None
    parser = None
    counters = Counter()
    buffers = {'parse_result':[]}
    parse_buffer_limit = 10000

    def __init__(self, db, parser):
        self.db = db
        self.parser = parser

    def get_counter(self,index):
        return self.counters[index]

    def clear_parse_buffer(self):
        self.db.addAdsense(self.buffers['parse_result'])
        del self.buffers['parse_result'][:]
        logging.debug('buffer put into DB')

    def success_domain_check(self, obj):
        self.counters['domain_check_success']+=1
        self.db.clearProps(obj.props['id_domain'])
        links = self.parser.parsePropLinks(obj.props['url'], obj.source.getvalue())
        if len(links):
            self.counters['find_links']+=len(links)
            self.db.addProps(obj.props['id_domain'], links)

    def error_domain_check(self, obj):
        self.counters['domain_check_fail']+=1
        self.db.clearProps(obj.props['id_domain'])


    def success_adsense_grab(self, obj):      
        res = self.parser.extractAdSense(obj.source.getvalue())
        if res == None :
            self.counters['links_grab_empty']+=1
        elif res == False:
            self.counters['links_grab_not_parse']+=1
        else:
            self.counters['links_grab_success']+=1
            if len(res):
                if len(self.buffers['parse_result']) < self.parse_buffer_limit:
                    self.buffers['parse_result'] += res
                else:
                    self.clear_parse_buffer()
    
    def error_adsense_grab(self, obj):
        self.counters['links_grab_fail']+=1
        

    def success_links_check(self, obj):
        if self.parser.linkStatusSuccess(obj.header.getvalue()) :
            self.counters['links_check_success']+=1

            cookie = self.parser.cookieParse(obj.header.getvalue())
            if cookie:
                self.db.linksCookieUpd(obj.props['id_link'],cookie)
            else:
                self.counters['links_check_cookie_error']+=1
        else:
            self.counters['links_check_not_ok']+=1
            self.db.delLink(obj.props['id_link'])
    
    def error_links_check(self, obj):
        self.counters['links_check_fail']+=1
        self.db.delLink(obj.props['id_link'])


def multi_get(urls, num_conn, timeout, err_callback, succ_callback, ua='semRushBot', percentile=100):
    result = {}
    queue = deque(list(urls))
    cur_percentile = 0
    print_percentile = 0
    
    if not queue: return
    
    num_urls = len(queue)
    num_conn = min(num_conn, num_urls)

    assert 1 <= num_conn <= 10000, "invalid number of concurrent connections"
    assert 1 <= percentile <= 100, "invalid percentile"

    logging.debug("PycURL %s (compiled against 0x%x)" % (pycurl.version, pycurl.COMPILE_LIBCURL_VERSION_NUM))

    m = pycurl.CurlMulti()
    m.handles = []
    for i in range(num_conn):
        c = pycurl.Curl()
        c.fp = None
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 1)
        c.setopt(pycurl.CONNECTTIMEOUT, timeout)
        c.setopt(pycurl.TIMEOUT, timeout)
        c.setopt(pycurl.NOSIGNAL, 1)
        c.setopt(pycurl.USERAGENT, ua)

        m.handles.append(c)

    freelist = m.handles[:]
    num_processed = 0
    bailout = 0
    while num_processed < num_urls:
        if bailout:
            break

        while queue and freelist:
            c = freelist.pop()
            c.props = queue.popleft()

            if type(c.props['url']) == type(u''):
                c.props['url'] = c.props['url'].encode('utf8', 'replace')

            c.setopt(pycurl.URL, c.props['url'])

            try:
                c.setopt(pycurl.COOKIE, str(c.props['cookie']))
            except KeyError:
                pass

            c.source = cStringIO.StringIO()
            c.header = cStringIO.StringIO()

            c.setopt(pycurl.HEADERFUNCTION, c.header.write)
            c.setopt(pycurl.WRITEFUNCTION, c.source.write)

            m.add_handle(c)

        while 1:
            ret, num_handles = m.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break

        while 1:
            num_q, ok_list, err_list = m.info_read()

            for c in ok_list:
                c.fp = None
                m.remove_handle(c)
                logging.debug("[ ok] %s" % (c.props['url']))
                succ_callback(c)
                freelist.append(c)

            for c, errno, errmsg in err_list:
                c.fp = None
                m.remove_handle(c)
                logging.debug("[err] %s %s" % (c.props['url'], errmsg))
                err_callback(c)
                freelist.append(c)

            num_processed = num_processed + len(ok_list) + len(err_list)

            if num_urls:
                cur_percentile = round(float(num_processed) / num_urls * 100)
                if cur_percentile % 10 == 0 and 0<cur_percentile<100 and print_percentile != cur_percentile:
                    logging.info("%d%%" % cur_percentile)
                    print_percentile = cur_percentile

                if (cur_percentile >= percentile):
                    bailout = 1
                    break
            if num_q == 0:
                break
        m.select(1.0)

    m.close()

    return result


if __name__ == '__main__':
    
    logging.basicConfig(filename='checker.log',
                        level=logging.INFO)

    try:
        import psyco
        psyco.full()
        logging.info("Psyco: Yes, im here =)")
    except ImportError:
        pass

    db = DB()
    parser = Parser()
    callbacks = Callbacks(db, parser)
    num_conn = 100

    #глобальный парсинг главных страниц всех доменов в БД на предмет кода гуглоаналитикса
    urls = db.getAllDomains()
    logging.info('found %d domains for checking' % len(urls))
    if len(urls)>0 :
        tt = time.time()
        multi_get(
            urls,
            num_conn = num_conn,
            timeout = 30,
            err_callback = callbacks.error_domain_check,
            succ_callback = callbacks.success_domain_check)
        logging.info('%f urls per second (%d url by %f sec and %d connections)' % (len(urls) / (time.time()-tt), len(urls), time.time()-tt, num_conn))
        logging.info('domains check counters: %d success, %d fail, %d links' %
                        (callbacks.get_counter('domain_check_success'), callbacks.get_counter('domain_check_fail'), callbacks.get_counter('find_links')) )

    #проверка всех существующих рекламных ссылок и удаление битых
    links = db.getAllLinks()
    logging.info('found %d links for checking' % len(links))

    if len(links)>0 :
        tt = time.time()
        multi_get(
            links,
            num_conn = num_conn,
            timeout = 15,
            err_callback = callbacks.error_links_check,
            succ_callback = callbacks.success_links_check)
        logging.info('%f urls per second (%d url by %f sec and %d connections)' % (len(links) / (time.time()-tt), len(links), time.time()-tt, num_conn))
        logging.info('links check counters: %d success, %d fail, %d error status, %d cookie error' %
                        (callbacks.get_counter('links_check_success'), callbacks.get_counter('links_check_fail'), callbacks.get_counter('links_check_not_ok'), callbacks.get_counter('links_check_cookie_error')) )


    db.close()
    
