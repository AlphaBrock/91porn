# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name   :    asyncSpider
   Description :    爬取91的视频信息
   Author      :    jccia
   date        :    2021/5/9
-------------------------------------------------
"""
import asyncio
import random
import re
from ipaddress import IPv4Address
from urllib.parse import unquote

import aiohttp
import requests as requests
from fake_useragent import UserAgent
from lxml import etree
from concurrent.futures import ThreadPoolExecutor, wait

from libs.downloader import DownLoader
from utils.logger import Logger
from utils.readSetting import Config

ua = UserAgent()
downloader = DownLoader()
log = Logger(filename="log/asyncSpider.log")


class Spider(Config):

    def __init__(self):
        super().__init__()
        self.max_threads = 10
        self.payload = {
            "session_language": "cn_CN"
        }

    @staticmethod
    def __parse_results(html):

        try:
            html = etree.HTML(html, etree.HTMLParser())
            return html
        except Exception as e:
            raise e

    def getPageNum(self, url):
        """
        获取网页数量
        :param url:
        :return:
        """
        headers = {
            "User-Agent": ua.random,
            "Host": self.pornHost,
            "referer": url,
            "X-Forwarded-For": str(IPv4Address(random.getrandbits(32)))
        }
        response = requests.request("POST", url, headers=headers, timeout=30)
        log.logger.debug(response.status_code)
        html = self.__parse_results(response.text)
        tmpPages = html.xpath("//div[contains(@class,'pagingnav')]/form/a/text()")
        pages = []
        for page in tmpPages:
            if page.isdigit():
                pages.append(int(page))
        log.logger.debug("总共页数:{}".format(max(pages)))
        return max(pages)

    def getVideoUrlList(self, pageUrl):
        """
        获取每页中的视频信息
        :param pageUrl:
        :return:
        """
        try:
            headers = {
                "User-Agent": ua.random,
                "Host": self.pornHost,
                "referer": pageUrl,
                "X-Forwarded-For": str(IPv4Address(random.getrandbits(32)))
            }
            response = requests.request("POST", pageUrl, headers=headers, data=self.payload, timeout=30)
            html = self.__parse_results(response.text)
            videoUrls = html.xpath("//div[contains(@class,'well well-sm videos-text-align')]/a/@href")
            videoThumbs = html.xpath("//div[contains(@class,'well well-sm videos-text-align')]/a/div/img/@src")
            videoTitles = html.xpath("//div[contains(@class,'well well-sm videos-text-align')]/a/span[contains(@class,'video-title title-truncate m-t-5')]/text()")
            videoDurations = html.xpath("//div[contains(@class,'well well-sm videos-text-align')]/a/div/span/text()")
            log.logger.info("videoTitle:{}, videoDuration:{}, videoUrl:{}, videoThumb:{}".format(videoTitles, videoDurations, videoUrls, videoThumbs))
            return videoTitles, videoDurations, videoUrls, videoThumbs
        except Exception as e:
            log.logger.exception(e)

    async def downloadHtml(self, session, url):
        """
        下载网页内容
        :param url:
        :return:
        """
        headers = {
            "User-Agent": ua.random,
            "Host": self.pornHost,
            "referer": url,
            "X-Forwarded-For": str(IPv4Address(random.getrandbits(32)))
        }
        async with session.get(url, headers=headers, timeout=60) as response:
            assert response.status == 200
            html = await response.read()
            return html

    async def getM38UUrl(self, session, url):
        text = await self.downloadHtml(session, url)
        try:
            videoEncodeUrl = re.compile(r'document.write\(strencode2\(([^)]+)').search(text.decode('utf-8')).group(1)
            log.logger.debug(unquote(videoEncodeUrl, encoding='utf-8', errors='replace'))
            videoDecodeUrl = re.compile(r'src=\'(http[a-z\.:0-9\/]+)').search(unquote(videoEncodeUrl, encoding='utf-8', errors='replace')).group(1)
            return videoDecodeUrl
        except Exception as e:
            log.logger.exception("获取视频链接:{}出错，抛出异常:{}".format(url, e))
            log.logger.error("视频链接:{}, 获取视频链接异常的网页信息:{}".format(url, text))
            return None

    async def handleTasks(self, task_id, work_queue):
        """
        异步获取m3u8地址
        :param task_id:
        :param work_queue:
        :return:
        """
        while not work_queue.empty():
            videoTitle, videoDuration, videoUrl, videoThumbUrl = await work_queue.get()
            try:
                async with aiohttp.ClientSession() as session:
                    videoDecodeUrl = await self.getM38UUrl(session, videoUrl)
                    if videoDecodeUrl:
                        downloader.run(videoDecodeUrl, videoThumbUrl, videoTitle=videoTitle, videoDuration=videoDuration)
                    else:
                        log.logger.exception(videoDecodeUrl)
                    log.logger.info(
                        "videoTitle:{}, videoDuration:{}, videoUrl:{}, videoThumb:{}".format(videoTitle, videoDuration, videoDecodeUrl, videoThumbUrl))
            except Exception as e:
                log.logger.exception("videoTitle:{}, videoDuration:{}, videoUrl:{}, videoThumb:{}, exception:{}".format(videoTitle, videoDuration, videoUrl, videoThumbUrl, e))

    def eventLoop(self, pageUrl):
        videoTitles, videoDurations, videoUrls, videoThumbs = self.getVideoUrlList(pageUrl)
        q = asyncio.Queue()
        [q.put_nowait((videoTitles[i], videoDurations[i], videoUrls[i], videoThumbs[i])) for i in range(len(videoTitles))]
        # loop = asyncio.new_event_loop()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            tasks = [self.handleTasks(task_id, q, ) for task_id in range(self.max_threads)]
            loop.run_until_complete(asyncio.wait(tasks))
        except RuntimeError as e:
            pass
        finally:
            loop.close()

    # def aa(self, loop, start, end):
    #     if start == 0:
    #         start += 1
    #
    #     while start < end:
    #         url = "{}&page={}".format(self.pornUrl, start)
    #         self.eventLoop(loop, url)
    #         start += 1

    def run(self):
        pageNum = self.getPageNum(self.pornUrl)

        # part = pageNum // 24
        # pool = ThreadPoolExecutor(max_workers=6)
        # futures = []
        # loop = asyncio.new_event_loop()
        # for i in range(24):
        #     start = part * i
        #     if i == 24 -1:
        #         end = pageNum
        #     else:
        #         end = start + part - 1
        #     log.logger.debug("startPageNum:{}, endPageNum:{}".format(start, end))
        #     futures.append(pool.submit(self.aa, loop, start, end))
        # wait(futures)
        for i in range(1, int(pageNum)):
            url = "{}&page={}".format(self.pornUrl, i)
            self.eventLoop(url)
