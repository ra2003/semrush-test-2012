#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__="esemi"

import logging
from db_operations import DB

if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)

    urls = [name.strip() for name in file('domains.txt') ]
    logging.info("Найдено %d домена" % len(urls))

    if( len(urls) > 0 ):
        db = DB()
        db.addUrls(urls)
        db.close()
        
