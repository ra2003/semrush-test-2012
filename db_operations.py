# -*- coding: utf-8 -*-

import logging
import sys

import MySQLdb as mdb

class DB():
    HOST = 'localhost'
    LOGIN = 'semrush'
    PASS = 'qwerty'
    DBNAME = 'semrush'

    _conn = None

    def __init__(self):        
        self.connect()

    def conn(self):
        return self._conn


    def connect(self):
        try:
            self._conn = mdb.connect(self.HOST, self.LOGIN, self.PASS, self.DBNAME, charset="utf8", use_unicode=True)
        except mdb.Error, e:
            logging.error("Error %d: %s" % (e.args[0], e.args[1]))
            sys.exit()
        logging.debug("Соединение mysql открыто")


    def close(self):
        if self.conn():
            self.conn().close()
            logging.debug("Соединение mysql закрыто")


    def addUrls(self, urls):
        cursor = self.conn().cursor()
        for url in urls:
            cursor.execute("INSERT IGNORE INTO `domains` (`url`) VALUES (%s)", (url))
        self.conn().commit()


    def getAllDomains(self):
        cursor = self.conn().cursor(mdb.cursors.DictCursor)
        cursor.execute("SELECT id as id_domain, url FROM `domains`")
        rows = cursor.fetchall()
        cursor.close()
        return rows


    def getAllLinks(self):
        cursor = self.conn().cursor(mdb.cursors.DictCursor)
        cursor.execute("SELECT id as id_link, link AS url,'test_cookie=CheckForPermission' AS cookie FROM `adsense_links`")
        rows = cursor.fetchall()
        cursor.close()
        return rows


    def clearProps(self, domain_id):
        cursor = self.conn().cursor()
        cursor.execute("DELETE FROM `adsense_links` WHERE `domain_id` = %s", domain_id )
        self.conn().commit()


    def addProps(self, domain_id, links):
        cursor = self.conn().cursor()
        for link in links:
            cursor.execute("INSERT INTO `adsense_links` (`domain_id`, `link`) VALUES (%s, %s)", (domain_id, link))
        self.conn().commit()


    def addAdsense(self, buffer_data):
        cursor = self.conn().cursor()
        for item in buffer_data:
            cursor.execute("INSERT IGNORE INTO `ads` (`title`, `desc`, `href`) VALUES (%s, %s, %s)",
                            (item['title'], item['desc'], item['url']))
        self.conn().commit()


    def getLinksForUpdate(self, count):
        cursor = self.conn().cursor(mdb.cursors.DictCursor)
        cursor.execute("""SELECT adsense_links.`id` as id_link , url as domain, `domain_id` as id_domain , `link` as url, `last_cookie` as `cookie` FROM `adsense_links` LEFT JOIN domains ON ( domain_id = domains.id ) WHERE last_cookie IS NOT NULL ORDER BY date_load LIMIT %s""", count)
        rows = cursor.fetchall()
        cursor.close()
        return rows


    def delLink(self, link_id):
        cursor = self.conn().cursor()
        cursor.execute("DELETE FROM `adsense_links` WHERE `id` = %s", link_id )
        self.conn().commit()

    def linksCookieUpd(self, link_id, cookie):
        cursor = self.conn().cursor()
        cursor.execute("UPDATE `adsense_links` SET `last_cookie` = %s WHERE `id` = %s", (cookie, link_id))
        self.conn().commit()

    def linksLoadUpd(self, ids):
        cursor = self.conn().cursor()
        for id in ids:
            cursor.execute("UPDATE `adsense_links` SET `date_load` = NOW() WHERE `id` = %s", (id))
        self.conn().commit()

    def addLoaderLog(self,count, sec, conn, succ, fail, not_ok, empty):
        cursor = self.conn().cursor()
        cursor.execute("""INSERT INTO `loader_counters` (`count_urls`, `seconds`, `connections`, `success`, `fail`, `not_parsed`, `empty_response`)
                        VALUES (%d,%.4f,%d,%d,%d,%d,%d)""" % (count, sec, conn, succ, fail, not_ok, empty))
        self.conn().commit()
