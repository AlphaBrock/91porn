# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name   :    logger
   Description :
   Author      :    jccia
   date        :    2021/5/10
-------------------------------------------------
"""
import logging
from logging import handlers


class Logger(object):
    """
    即在终端打印日志也在文件中打印日志
    """
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'crit': logging.CRITICAL
    }

    def __init__(self, filename, level='debug', when='D', backCount=3,
                 fmt='[%(asctime)s] [%(levelname)s] [%(filename)s:%(module)s.%(funcName)s:%(lineno)d] [%(process)d] %(message)s'):
        self.logger = logging.getLogger(filename)
        format_str = logging.Formatter(fmt)
        self.logger.setLevel(self.level_relations.get(level))
        sh = logging.StreamHandler()
        sh.setFormatter(format_str)
        th = handlers.TimedRotatingFileHandler(filename=filename, when=when, backupCount=backCount,
                                               encoding='utf-8')
        th.setFormatter(format_str)
        self.logger.addHandler(sh)
        self.logger.addHandler(th)
