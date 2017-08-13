#!/usr/bin/env python

'''
Version: 0.2
Author: haotie
Desciption: 抓取豆瓣一拍一所有客片
'''

import urllib.request as req
import requests
import shutil
import bs4
import re
import os
import threading
import redis


home_url = "https://ypy.douban.com"
start_url = home_url + "/explore"
result_dir_name = "/mnt/storage/images"  # 存储图片的目录
#result_dir_name = "douban-ypy"  # 存储图片的目录
r = redis.StrictRedis(host='localhost', port=6379, db=0)
r.setnx('current', 0)
r.setnx('total', 0)

def total_albums(soup):
    tags_num = [int(e.text) for e in soup.find_all('em')]
    return sum(tags_num)


#def show_progress(current, total):
#    print('进度{:.1f}% 当前是第{}个相册, 剩余{}个'.format(
#        current / total * 100, current, total - current))

def show_progress():
    current = int(r.get('current'))
    total = int(r.get('total'))
    print('进度{:.1f}% 当前是第{}个相册, 剩余{}个'.format(
        current / total * 100, current, total - current))

def down_photo_of_a_album(album_path, urls):
    print('正在下载此相册的{}张照片'.format(len(urls)))

    # 为每张照片的下载开辟一个线程
    threads = []
    for photo in urls:
        #        req.urlretrieve(photo, album_path +'/' + os.path.basename(photo))
        #t = threading.Thread(target=req.urlretrieve, args=(photo, album_path + '/' + os.path.basename(photo) + '.jpeg'))
        t = threading.Thread(target=down_img, args=(photo, album_path + '/' + os.path.basename(photo) + '.jpeg'))
        threads.append(t)
        t.start()

def down_img(url, path):
    if os.path.exists(path):
        return
    if not r.get(url):
        r.set(url, path)
    else:
        if os.path.exists(path):
            return
    response = requests.get(url, stream=True, proxies=proxies)
    with open(path, 'wb') as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response



def down_album_of_a_tag(urls, tag_dir_name):
    album_url_set = set()
    for album in urls:
        album_name = album.getText().split()[0].strip('。').replace('/', '_')
        album_url = home_url + album.attrs['href']
        # need attention
        if album_url not in album_url_set:
            album_url_set.add(album_url)
            album_path = tag_dir_name + '/' + album_name
            if not os.path.exists(album_path):
                album_path += album_url.split('/')[-1]
                album_name += album_url.split('/')[-1]
            try:
                os.mkdir(album_path)
            except FileExistsError:
                pass
        else:
            continue

        album_soup = bs4.BeautifulSoup(req.urlopen(album_url), 'lxml')
        #album_soup = bs4.BeautifulSoup(requests.get(album_url, proxies=proxies).content, 'lxml')
        album_photo = album_soup.find_all('script', text=re.compile('_PHOTOS'))
        regex = re.compile(r'https://qnypy.doubanio.com/[^"]+')
        photo_url = regex.findall(str(album_photo))
        print('正在下载相册<<{}>>'.format(album_name))
        #global current, total
        #show_progress(current, total)
        show_progress()

        #current += 1
        r.incr('current')
        down_photo_of_a_album(album_path, photo_url)


def preprocessing():
    '''预处理, 清理文件等'''
    #if os.path.exists(result_dir_name):
    #    import shutil
    #    shutil.rmtree(result_dir_name)

    #if not os.path.exists(result_dir_name):
    #    os.mkdir(result_dir_name)
    os.chdir(result_dir_name)


def spider():
    '''
    按照 "标签(tag) -> 相册(album) -> 照片(photo)" 的层次获取照片
    每个标签建立一个目录, 此目录里, 为每个相册又建立一个目录
    '''
    soup = bs4.BeautifulSoup(req.urlopen(start_url), 'lxml')
    #soup = bs4.BeautifulSoup(requests.get(start_url, proxies=proxies).content, 'lxml')
#    global total
#    total = total_albums(soup)
    r.set('total', total_albums(soup))
    all_tags_url = soup.findAll('a', {'class': 'tag'})
    down_all_tags(all_tags_url)


def down_all_tags(all_tags_url):
    for tag in all_tags_url:
        tag_dir_name = tag.getText().split()[0].replace('/', '_')
        try:
            os.mkdir(tag_dir_name)
        except FileExistsError:
            pass

        tag_html = home_url + tag.attrs['href']
        tag_soup = bs4.BeautifulSoup(req.urlopen(tag_html), 'lxml')
        #tag_soup = bs4.BeautifulSoup(requests.get(tag_html, proxies=proxies).content, 'lxml')
        tag_urls = tag_soup.findAll('a', {'class': 'album-item-a'})

        down_album_of_a_tag(tag_urls, tag_dir_name)


if __name__ == '__main__':
    preprocessing()
    spider()
