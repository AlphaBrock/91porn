# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name   :    main
   Description :    主函数入口
   Author      :    jccia
   date        :    2021/5/11
-------------------------------------------------
"""
import os
from utils.sqlite import Database
from libs.asyncSpider import Spider


def main():
    if not os.path.exists("91porn.db"):
        db = Database()
        db.initDb()

    spider = Spider()
    spider.run()


if __name__ == '__main__':
    main()
