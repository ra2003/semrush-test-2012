#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import time
from parser import Parser

from checker import Callbacks, multi_get
from db_operations import DB


if __name__ == "__main__":

    logging.basicConfig(filename='loader.log',
                        level=logging.INFO)
    
    try:
        import psyco
        psyco.full()
        logging.info("Psyco: Yes, im here =)")
    except ImportError:
        pass

    reload(sys)
    sys.setdefaultencoding("utf8")
    
    num_conn = 200
    count_links = 1000
    link_repeat = 100

    db = DB()
    links = db.getLinksForUpdate(count_links)
    logging.info("found %d links for update" % len(links))
    if(len(links) > 0):
        parser = Parser()
        callbacks = Callbacks(db, parser)
        
        db.linksLoadUpd([link['id_link'] for link in links])
        urls = [link for i in range(link_repeat) for link in links] 
        logging.info("compute %d urls for loading" % len(urls))
        
        tt = time.time()
        multi_get(urls, num_conn,
                  timeout=8,
                  err_callback=callbacks.error_adsense_grab,
                  succ_callback=callbacks.success_adsense_grab)
        callbacks.clear_parse_buffer()
        logging.info('%f urls per second (%d url by %f sec and %d connections)' % (len(urls) / (time.time()-tt), len(urls), time.time()-tt, num_conn))
        logging.info('links parse counters: %d success, %d fail, %d not parse, %d empty response' %
                     (callbacks.get_counter('links_grab_success'),
                     callbacks.get_counter('links_grab_fail'),
                     callbacks.get_counter('links_grab_not_parse'),
                     callbacks.get_counter('links_grab_empty')))
        db.addLoaderLog(
                len(urls), time.time()-tt, num_conn,
                callbacks.get_counter('links_grab_success'),
                callbacks.get_counter('links_grab_fail'),
                callbacks.get_counter('links_grab_not_parse'),
                callbacks.get_counter('links_grab_empty'))

    db.close()
