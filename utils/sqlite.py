# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name   :    sqlite
   Description :
   Author      :    jccia
   date        :    2021/5/11
-------------------------------------------------
"""
import sqlite3
import threading
from utils.readSetting import Config
from utils.logger import Logger

sqliteMutex = threading.Lock()

log = Logger(filename="log/sqlite.log")


class Database(Config):

    def __init__(self):
        super(Database, self).__init__()

    def initDb(self):
        con = sqlite3.connect(self.dbPath)
        dbTable = "defaultVideo"
        videoInfo = '''CREATE TABLE IF NOT EXISTS %s
                (
                  id  INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                  videoId    VARCHAR(20),
                  videoTitle    VARCHAR(20),
                  videoUrl    VARCHAR(20),
                  videoDuration VARCHAR(20),
                  videoPic   VARCHAR(20),
                  date TIMESTAMP NOT NULL DEFAULT (datetime('now','localtime'))
                );
        ''' % dbTable

        cur = con.cursor()
        cur.execute(videoInfo)
        con.commit()
        con.close()

    def select(self, sql):
        """
        select 操作，加锁防止deadlock
        :param sql:
        :return:
        """
        with sqliteMutex:
            con = sqlite3.connect(self.dbPath)
            cur = con.cursor()
            cur.execute(sql)
            con.close()
            return cur

    def insert(self, sql):
        """
        insert 操作，加锁防止deadlock
        :param sql:
        :return:
        """
        with sqliteMutex:
            con = sqlite3.connect(self.dbPath)
            cur = con.cursor()
            try:
                cur.execute(sql)
                con.commit()
            except Exception as e:
                log.logger.exception("sql:{}, 运行异常:{}".format(sql, e))
                con.rollback()
            finally:
                con.close()
