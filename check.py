# coding=utf-8
#

import os
import re
import requests
import threading
from datetime import datetime
from requests import RequestException
from time import sleep


BASE_DIR = os.path.dirname(__file__)
IP_TXT = os.path.join(BASE_DIR, datetime.now().strftime('%Y-%m-%d') + '-ip.txt')
SCR_IP_TXT = os.path.join(BASE_DIR, 'ip.txt')

MAX_TEST_THREADS = 100


class TestThread(threading.Thread):
    def __init__(self, _ip_li):
        self.li = _ip_li
        super(TestThread, self).__init__()

    def run(self):
        self.li = [_ for _ in self.li if self.test_ip_available(_)]

    def test_ip_available(self, ip):
        _proxy = {'https': ip}
        try:
            print (u'正在检测IP: %s 有效性\n' % ip)
            r = requests.get('https://www.so.com/s?ie=utf-8&fr=none&src=360sou_newhome&q=123', 
                             proxies=_proxy,
                             timeout=5)
            assert u'_360搜索' in r.text
        except (RequestException, AssertionError):
            return False
        print (u'找到可用代理IP: %s\n' % ip)
        return True


def time_wrapper(func):
    def _wrapper():
        start_time = datetime.now()
        func()
        end_time = datetime.now()
        seconds = (end_time - start_time).total_seconds()
        print (u'本次执行共消耗: %d分%d秒\n' % (seconds / 60, seconds % 60))
    return _wrapper


@time_wrapper
def parse_ip():
    # 读取本地ip文件
    with open(SCR_IP_TXT) as f:
        _ip_list = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', f.read())
    print (u'检索到: %d 个IP地址\n' % len(_ip_list))

    # 平均分配_ip_list到各个线程检测
    threads = []
    avg = len(_ip_list) // MAX_TEST_THREADS
    if len(_ip_list) % MAX_TEST_THREADS != 0:
        avg += 1
    for i in range(MAX_TEST_THREADS):
        _thread = TestThread(_ip_list[i*avg:(i+1)*avg])
        threads.append(_thread)
        _thread.start()

    # 等待所有检测线程退出
    while threading.active_count() > 1:
        sleep(10)

    # 读取所有有效IP并写入文件
    _ip_list = []
    for th in threads:
        _ip_list.extend(th.li)

    _ip_list = set(_ip_list)
    print (u'\n总共找到 %d 个可用IP\n' % len(_ip_list))
    with open(IP_TXT, 'w') as f:
        f.write('\n'.join(_ip_list))


if __name__ == '__main__':
    parse_ip()

