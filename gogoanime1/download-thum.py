import os
import requests
import numpy as np
import time
import subprocess
import json
from bs4 import BeautifulSoup
# from moviepy.editor import VideoFileClip
import re

np.seterr(over='ignore')
key_api = "AIzaSyAdO-hmFHLaRgiARrMRNdpN9RqgYx_ulB4"

pwd = os.getcwd()
pwd = pwd + '/'


def get_list_video_by_api(channel_id, stt_id):
    results = []
    max_result = 50
    page_token = ''

    while len(results) < 51:
        url = "https://www.googleapis.com/youtube/v3/search?part=id&key=" \
              + str(key_api) + "&channelId=" + str(channel_id) + "&maxResults=" + str(max_result) \
              + "&order=date&pageToken=" + str(page_token)

        req = requests.get(url)

        list_item = json.loads(req.content)
        items = list_item['items']

        try:
            page_token = list_item['nextPageToken']
        except KeyError:
            page_token = ''

        for item in items:
            try:
                id_video = item['id']['videoId']
            except KeyError:
                id_video = ''

            if id_video != '':
                results.append(id_video)

        if page_token == '':
            break

    return results


def get_list_video_by_html(channel_id):
    results = []
    max_result = 30
    url = "https://www.youtube.com/channel/" + str(channel_id) + "/videos"
    req = requests.get(url)
    content = BeautifulSoup(req.content, "lxml")
    items = content.find_all(class_="yt-lockup-content")
    stt = 1
    print(content)

    for item in items:
        if max_result < stt:
            break

        a = item.find("a")
        id_video = a.get('href').replace("/watch?v=", "")
        results.append(id_video)
        stt = stt + 1

    return results


def get_list_video(channel_id, length_cut, stt_id):
    print("Get list video..")

    option = input("Option: ")

    if option == 'reup':
        items = get_list_video_by_api(channel_id, stt_id)
    else:
        items = get_list_video_by_html(channel_id)
    stt = 1

    for id_video in items:
        stt = get_thumbnail("https://www.youtube.com/watch?v=" + str(id_video), stt)


def remove_special_characters(string):
    # string = string.replace('\r', '')
    # string = string.replace(' : ', '-')
    # string = string.replace(' ', '-')
    # string = string.replace('.', '-')
    #
    # return re.sub(r'[^a-zA-Z0-9-\n\.]', '', string)
    string = string.replace('\r', '')
    string = string.replace('[', '')
    string = string.replace(']', '')
    string = string.replace('|', '')
    string = string.replace('-', '')

    return string


def get_number_video(url):
    try:
        stdout = subprocess.check_output(['youtube-dl', '-F', url])
        arr = str(stdout).split('\\n')

        audio = ''

        for item in arr:
            if 'm4a' in item:
                audio = item.split(' ')[0]

        for item in arr:
            if '720' in item and 'mp4' in item:
                return str(item.split(' ')[0]) + '+' + str(audio)

        for item in arr:
            if '480' in item and 'mp4' in item:
                return str(item.split(' ')[0]) + '+' + str(audio)

        for item in arr:
            if '360' in item and 'mp4' in item:
                return str(item.split(' ')[0]) + '+' + str(audio)

        for item in arr:
            if '240' in item and 'mp4' in item:
                return str(item.split(' ')[0]) + '+' + str(audio)
    except:
        return False

    return True


def get_thumbnail(url, stt):

    try:
        stdout = subprocess.check_output(['youtube-dl', '--list-thumbnails', url])

        arr = str(stdout).split('\\n')
        url = ''

        for i in arr:
            temp = re.findall(r'http(.*?).jpg', str(i))

            if len(temp) > 0:
                url = 'http' + temp[0] + '.jpg'

        if url == '':
            return ''

        r = requests.get(url)

        if r.status_code == 200:
            with open(str(stt) + '.jpg', 'wb') as file:
                for chunk in r.iter_content(1024):
                    file.write(chunk)
    except:
        return stt + 1

    return stt + 1


if __name__ == '__main__':
    get_list_video('UCxZPAntRm3rJH09H0aF3hVw', '0','0')
