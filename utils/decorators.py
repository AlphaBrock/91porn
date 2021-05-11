# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name   :    decorators
   Description :
   Author      :    jccia
   date        :    2021/5/11
-------------------------------------------------
"""
from functools import wraps
from utils.sqlite import Database

db = Database()


def insertDataToDb(func):

    @wraps(func)
    def decorator(self, url):
        fileName, urls, files = func(self, url)

    return decorator

