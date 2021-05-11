# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name   :    downloader
   Description :    91视频与封面下载，通篇采用了低端的retry机制保证下载和上传的成功率
   Author      :    jccia
   date        :    2021/5/9
-------------------------------------------------
"""
import base64
import os
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, wait
from ipaddress import IPv4Address

import requests
from fake_useragent import UserAgent

from utils.github import Github
from utils.logger import Logger

ua = UserAgent()
github = Github()
log = Logger(filename="../log/downloader.log")


class DownLoader(object):

    def __init__(self):
        if not os.path.exists("../video"):
            os.mkdir("../video")

    def m3u8s(self, url, **kwargs):
        """
        从m3u8文件中提取数据
        :param url:
        :return:
        """
        headers = {
            "User-Agent": ua.random,
            "Host": "91porn.com",
            "X-Forwarded-For": str(IPv4Address(random.getrandbits(32)))
        }
        baseUrl = re.compile(r'(.*)/[0-9]+\.m3u8').search(url).group(1)
        fileName = re.compile(r'/([0-9]+)\.m3u8').search(url).group(1)
        if not os.path.exists("video/{}".format(fileName)):
            os.mkdir("video/{}".format(fileName))

        i = 0
        while i < 3:
            r = requests.request("GET", url, headers=headers)
            if r.status_code != 400:
                with open("video/{}/{}.m38u".format(fileName, fileName), "wb") as fp:
                    fp.write(r.content)

                uploadUrl = github.uploadFile(fileName, "{}.m3u8".format(fileName), base64.b64encode(r.content))
                if uploadUrl:
                    log.logger.info("videoTitle:{}, videoDuration:{}, videoUrl:{}".format(kwargs.get("videoTitle"),
                                                                                          kwargs.get("videoDuration"),
                                                                                          uploadUrl))

                with open("video/{}/{}.m38u".format(fileName, fileName), "rb+") as file:
                    urls = []
                    files = []
                    lines = file.readlines()
                    for line in lines:
                        if line.endswith(b".ts\n"):
                            urls.append(baseUrl + "/" + str(line.strip(b"\n")).replace("\'", "").replace("b", ""))
                            files.append(str(line.strip(b"\n")).replace("\'", "").replace("b", ""))

                return fileName, urls, files
            time.sleep(random.randint(2, 3))
            i += 1
            log.logger.warning("url:{}, 下载异常, 返回结果:{}, 重试次数:{}".format(url, r.text, i))

    def downVideo(self, tsFileName, tsUrl, file):
        """
        下载视频文件和缩略图
        :param tsFileName:
        :param tsUrl:
        :param file:
        :param thumbUrl:
        :return:
        """
        headers = {
            "User-Agent": ua.random,
            "X-Forwarded-For": str(IPv4Address(random.getrandbits(32)))
        }
        i = 0
        while i < 3:
            r = requests.request("GET", tsUrl, headers=headers)
            if r.status_code == 200:
                log.logger.info("下载ts文件:{}成功, 返回状态码:{}".format(file, r.status_code))
                github.uploadFile(tsFileName, file, base64.b64encode(r.content))
                break
            time.sleep(random.randint(2, 5))
            i += 1
            log.logger.warning("File:{}, 上传失败, 返回结果:{}, 重试次数:{}".format(file, r.status_code, i))

    def downThumb(self, tsFileName, thumbUrl, **kwargs):
        headers = {
            "User-Agent": ua.random,
            "X-Forwarded-For": str(IPv4Address(random.getrandbits(32)))
        }
        thumbFileName = re.compile(r'/([0-9]+\.[a-z]+)').search(thumbUrl).group(1)

        i = 0
        while i < 3:
            r = requests.request("GET", thumbUrl, headers=headers)
            if r.status_code == 200:
                uploadUrl = github.uploadFile(tsFileName, thumbFileName, base64.b64encode(r.content))
                if uploadUrl:
                    log.logger.info("videoTitle:{}, videoDuration:{}, videoThumbUrl:{}".format(kwargs.get("videoTitle"),
                                                                                               kwargs.get(
                                                                                                   "videoDuration"),
                                                                                               uploadUrl))

            time.sleep(random.randint(2, 5))
            i += 1
            log.logger.warning("thumbUrl:{}, 上传失败, 返回结果:{}, 重试次数:{}".format(thumbUrl, r.status_code, i))

    def run(self, m3u8Url, thumbUrl, **kwargs):
        """
        下载器主函数
        :param m3u8Url:
        :param thumbUrl:
        :return:
        """
        pool = ThreadPoolExecutor(max_workers=20)
        futures = []
        tsFileName, tsUrls, tsFiles = self.m3u8s(m3u8Url, **kwargs)
        if tsFileName:
            self.downThumb(tsFileName, thumbUrl, **kwargs)
            for i in range(len(tsUrls)):
                tsUrl = tsUrls[i]
                tsFile = tsFiles[i]
                futures.append(pool.submit(self.downVideo, tsFileName, tsUrl, tsFile))
                time.sleep(random.random())
            wait(futures)
