# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name   :    main
   Description :    主函数入口
   Author      :    jccia
   date        :    2021/5/11
-------------------------------------------------
"""

from libs.asyncSpider import Spider


if __name__ == '__main__':
    spider = Spider()
    spider.run()
