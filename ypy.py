#!/usr/bin/env python

'''
Version: 0.1
Desciption: 抓取豆瓣一拍一所有客片
'''

import urllib.request as req
import bs4
import re
import os

home_url = "https://ypy.douban.com"
start_url = home_url + "/explore"
result_dir_name = "douban-ypy"  # 存储图片的目录

def init_file_store():
    if not os.path.exists( result_dir_name ):
        os.mkdir( result_dir_name )
    os.chdir( result_dir_name )

def total_albums(soup):
    tags_num = [int(e.text) for e in soup.find_all('em')]
    return sum(tags_num)

def show_progress(current, total):
    print('进度{:.1f}% 当前是第{}个相册, 剩余{}个'.format(current / total * 100, current, total-current))


def download_photo():
    '''
    按照 "标签(tag) -> 相册(album) -> 照片(photo)" 的层次获取照片
    每个标签建立一个目录, 此目录里, 为每个相册又建立一个目录
    '''
    soup = bs4.BeautifulSoup(req.urlopen(start_url), 'lxml')
    total = total_albums(soup)
    current = 1
    category_by_tag = soup.findAll('a',{'class':'tag'})
    for tag in category_by_tag:
        tag_dir_name = tag.getText().split()[0]
        if not os.path.exists( tag_dir_name ):
            os.mkdir( tag_dir_name )
        
        tag_url = home_url + tag.attrs['href']
        tag_soup = bs4.BeautifulSoup(req.urlopen(tag_url), 'lxml')
        tag_soup_album = tag_soup.findAll('a', {'class':'album-item-a'})
        for album in tag_soup_album:
            album_name = album.getText().split()[0].strip('。')
            album_url = home_url + album.attrs['href']
            album_path = tag_dir_name + '/' + album_name
            if  os.path.exists( album_path ):
                album_path += album_url.split('/')[-1]
                album_name += album_url.split('/')[-1]
            os.mkdir( album_path )

            album_soup = bs4.BeautifulSoup(req.urlopen(album_url), 'lxml')
            album_photo =album_soup.find_all('script', text=re.compile('_PHOTOS'))
            regex = re.compile(r'https://qnypy.doubanio.com/[^"]+')
            photo_url = regex.findall(str(album_photo))

            print('正在下载相册<<{}>>'.format(album_name))
            show_progress(current, total)
            current += 1
            
            print('正在下载此相册的{}张照片'.format(len(photo_url)))
            for photo in photo_url:
                req.urlretrieve(photo, album_path +'/' + os.path.basename(photo))
            print('-' * 50)


if __name__ == '__main__':
    if os.path.exists( result_dir_name ):
        import shutil
        shutil.rmtree( result_dir_name )

    init_file_store()
    download_photo()
