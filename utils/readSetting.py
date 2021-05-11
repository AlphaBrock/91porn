# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name   :    readSetting
   Description :    读取配置文件
   Author      :    jccia
   date        :    2021/5/11
-------------------------------------------------
"""
import configparser

conf = configparser.ConfigParser()


class Config(object):

    def __init__(self):
        cfg = "../config.ini"
        conf.read(cfg)

        self.githubUserName = conf.get("github", "UserName")
        self.githubRepository = conf.get("github", "Repository")
        self.githubAccessToken = conf.get("github", "AccessToken")

        self.pornUrl = conf.get("91porn", "url")