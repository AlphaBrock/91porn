# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name   :    github
   Description :    github接口操作
   Author      :    jccia
   date        :    2021/5/11
-------------------------------------------------
"""
import requests
import random
import time
import json
from ipaddress import IPv4Address
from utils.logger import Logger
from utils.readSetting import Config

log = Logger("log/github.log")


class Github(Config):

    def __init__(self):
        super().__init__()
        # self.username = UserName
        # self.repository = Repository
        self.params = {
            "access_token": self.githubAccessToken
        }
        self.headers = {
            'Content-Type': 'application/json',
            "Authorization": "token {}".format(self.githubAccessToken)
        }

    def checkRepoSize(self):
        """
        检查仓库大小，考虑到后续超1G后切换仓库
        :return:
        """
        url = "https://api.github.com/repos/{}/{}".format(self.githubUserName, self.githubRepository)
        self.headers["X-Forwarded-For"] = str(IPv4Address(random.getrandbits(32)))
        try:
            response = requests.request("GET", url, headers=self.headers)
            assert response.status_code == 200
            return int(response.json()["size"])
        except Exception as e:
            log.logger.exception(e)
            return None

    def createRepo(self):
        """
        新建github仓库
        :return:
        """
        url = "https://api.github.com/{}/repos".format(self.githubUserName)
        self.headers["X-Forwarded-For"] = str(IPv4Address(random.getrandbits(32)))
        payload = {
            "name": "{}{}".format(self.githubRepository, random.randint(1, 10))
        }

        try:
            response = requests.request("GET", url, headers=self.headers, data=json.dumps(payload))
            assert response.status_code == 200
            log.logger.debug(response.text)
        except Exception as e:
            log.logger.exception(e)
            return None

    def uploadFile(self, FileName, File, Content):
        """
        上传文件至github
        :param FileName:
        :param File:
        :param Content:
        :return:
        """
        url = "https://api.github.com/repos/{}/{}/contents/{}/{}".format(self.githubUserName, self.githubRepository, FileName, File)
        payload = {
            "message": "upload by spider",
            "committer": {
                "name": self.githubUserName,
                "email": "915617545@qq.com"
            },
            "content": bytes.decode(Content)
        }
        self.headers["X-Forwarded-For"] = str(IPv4Address(random.getrandbits(32)))
        # socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1080)
        # socket.socket = socks.socksocket
        i = 0
        while i < 5:
            response = requests.request("PUT", url, headers=self.headers, data=json.dumps(payload))
            if response.status_code == 201 or response.status_code == 200:
                log.logger.info("File:{}, 上传成功".format(File))
                url = "https://cdn.jsdelivr.net/gh/{}/{}/{}/{}".format(self.githubUserName, self.githubRepository, FileName, File)
                log.logger.info(url)
                return url

            time.sleep(random.randint(2, 5))
            i += 1
            log.logger.warning("File:{}, 上传失败, 返回状态码结果:{}, 返回结果:{}, 重试次数:{}".format(File, response.status_code, response.text, i))