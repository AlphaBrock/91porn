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


class Config(object):

    def __init__(self):
        self.conf = configparser.ConfigParser()
        cfg = "config.ini"
        self.conf.read(cfg)

        self.githubUserName = self.conf.get("github", "UserName")
        self.githubRepository = self.conf.get("github", "Repository")
        self.githubAccessToken = self.conf.get("github", "AccessToken")

        self.pornUrl = self.conf.get("91porn", "url")
        self.pornHost = self.conf.get("91porn", "host")

        self.dbPath = self.conf.get("sqlite", "path")


if __name__ == '__main__':
    a = Config()