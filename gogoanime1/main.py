import requests
from bs4 import BeautifulSoup
import lxml
import lxml.html
import json
import os
import datetime
import subprocess
import re
import time
from lxml import html


def get_video(url, file_name, stt_id):
    path_file = ".mp4"
    r = requests.get(url, stream=True)  # create HTTP response object
    with open(str(stt_id) + "\\downloads\\" + str(file_name) + str(path_file), 'wb') as f:
        for chunk in r.iter_content(chunk_size=2048):
            if chunk:
                f.write(chunk)

    return True


def download_video_by_youtube_dl(url, stt_id):
    cmd = "youtube-dl -o " + str(stt_id) + "/downloads/input.%(ext)s '" + str(url) + "'"
    os.system(cmd)

    return True


def upload_youtube_and_check_out_number(title, description, tags, playlist, file_name):
    process = subprocess.Popen(['python', 'youtube-upload', '--title=' + str(title) + '', '--tags=' + tags + '', '--description=' + description + '', '--playlist=' + playlist + '', '--client-secrets=client_secrets.json', '--credentials-file=credentials.json', file_name], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()
    print(stdout)

    return 'Video URL' in stdout


def get_source_links(stt_id):
    # read file get arr website avail
    fo = open(stt_id + "/source-links.txt", "r")
    arr_website_avail = []
    lines = fo.readlines()

    for line in lines:
        arr_website_avail.append(line.replace('\n', ''))
    fo.close()

    return arr_website_avail


def check_exist_chapt(id_series, id_chapt_new, stt_id):
    name_file = stt_id + "/save-data.txt"

    fo = open(name_file, "r")

    lines = fo.readlines()
    # format series:chapt,chapt\n
    for line in lines:
        arr_split = line.split(':')
        if (len(arr_split) > 1):
            series_current = arr_split[0]
            list_chapt_current = arr_split[1].replace('\n', '').split(',')

            if (str(series_current) == str(id_series)):
                if str(id_chapt_new) in list_chapt_current:
                    return False
    fo.close()
    return True


def save_to_file(id_series, id_chapt_new, stt_id):
    name_file = stt_id + "/save-data.txt"

    fo = open(name_file, "r")
    lines = fo.readlines()
    check = True
    i = 0
    len_lines = len(lines)
    n = '\n'
    # format series:chapt,chapt\n
    for line in lines:
        arr_split = line.split(':')
        if (len(arr_split) > 1):
            series_current = arr_split[0]
            list_chapt_current = arr_split[1].replace('\n', '')

            if (i == len_lines - 1):
                n = ''
            if (str(series_current) == str(id_series)):
                list_chapt_current = str(id_series) + ':' + str(list_chapt_current) + ',' + str(id_chapt_new) + n
                lines[i] = list_chapt_current
                check = False
        i = i + 1
    if (check):
        if (len(lines) > 0):
            lines[len(lines) - 1] = lines[len(lines) - 1] + '\n'
        lines.append(str(id_series) + ':' + id_chapt_new)
    fo.close()

    fo = open(name_file, "w")
    fo.writelines(lines)
    fo.close()
    return True


# def isFirstUpload(stt_id):
#     f = open(stt_id + '/credentials.json', 'r')
#     lines = f.readlines()
#     f.close()
#     if(len(lines) == 0):
#         return True
#
#     return False
#
#
# def get_new_video(id_series, stt_web):


def download_video(url, stt_id):
    arr = get_url(url)

    if arr is False:
        return False

    check = get_video(str(arr['link']), 'input', str(stt_id))

    return arr


def get_url(url):
    print(url)
    # try:
    req = requests.get(url)

    root = html.fromstring(req.content)
    links = root.xpath('//html/body/div[2]/div[4]/div/div[2]/div[2]/div[4]/a[2]/@href')

    if len(links) == 0:
        links = root.xpath('/html/body/div[2]/div[4]/div/div[2]/div[2]/div[4]/a/@href')


    if len(links) == 0:
        return False

    link = links[0]
    print(link)
    # "/html/body/div[2]/div[4]/div/div[2]/div[2]/div[4]/a"

    # except IndexError:
    #     print("Link not found!")
    #
    #     return False

    title = root.xpath('//html/body/div[2]/div[4]/div/div[5]/div[1]/div/div/a/h3/text()')[0]
    des = root.xpath('//*[@id="showMoreDesc"]/text()')[0]
    genres = root.xpath('//html/body/div[2]/div[4]/div/div[5]/div[1]/div/div/table/tbody/tr/td/a/text()')
    genres = ','.join(genres)
    title = title.replace('\n', '').replace('\r', '').strip()
    des = des.replace('\n', '').replace('\r', '').strip()
    genres = genres.replace('\n', '').replace('\r', '').strip()

    return {
        'link': link,
        'title': title,
        'des': des,
        'genres': genres
    }



def isFirstUpload(stt_id):
    f = open(stt_id + '/credentials.json', 'r')
    lines = f.readlines()
    f.close()
    if(len(lines) == 0):
        return True

    return False


def get_new_video(id_series, stt_id, black_lists):
    url = "https://www.gogoanime1.com/watch/" + str(id_series)
    req = requests.get(url)
    root = html.fromstring(req.content)
    link = root.xpath('//html/body/div[2]/div[4]/div/div[3]/div[1]/div/div/ul/li[1]/a/@href')[0]
    index = link.rfind('/')
    eps = link[index + 1:]

    check = check_exist_chapt(id_series, eps, stt_id) and id_series not in black_lists

    if check:
        return {
            'link': link,
            'eps': eps
        }

    return False


def get_black_lists(stt_id):
    results = []
    name_file = str(stt_id) + "/blacklists.txt"

    fo = open(name_file, "r")

    lines = fo.readlines()

    for line in lines:
        item = line.replace('\n', '')
        results.append(item)

    fo.close()

    return results


def get_info_genres(id_series):
    url = 'http://animepill.com/anime/' + str(id_series)

    req = requests.get(url)
    root = html.fromstring(req.content)

    category = root.xpath('//div[@class="p-4"]/a/text()')
    genres = ','.join(category)

    return genres


def handle(url, eps, stt_id):
    print("Downloading...")

    arr_info = download_video(url, stt_id)

    if arr_info is False:
        return False

    title = arr_info['title'] + ' ' + str(eps)
    description = arr_info['des']
    description = description.replace('\"', '\'')
    genres = arr_info['genres']

    print("Processing...")

    os.system('ffmpeg -noaccurate_seek -ss 00:12:00 -i '
              + str(stt_id) + '\\downloads\\input.mp4 -to 00:01:30 -c copy '
              + str(stt_id) + '\\downloads\\output.mp4')

    start = datetime.datetime.now()

    file_name = str(stt_id) + '\\downloads\\output.mp4'

    print('Uploading...')
    # (isFirstUpload(stt_id))
    if True:
        os.system('youtube-upload --title="' + str(title)
                  + '" --description="' + description + '" --tags="' + str(genres) + '" '
                  + '--client-secrets=client_secrets.json --credentials-file='
                  + str(stt_id) + '/credentials.json ' + str(file_name))

        check = True
    else:
        check = upload_youtube_and_check_out_number(title, description, '', str(file_name), stt_id)

    os.remove(str(stt_id) + '\\downloads\\input.mp4')
    os.remove(file_name)

    end = datetime.datetime.now()
    print(end - start)

    return check


def get_series():
    result = []
    stt = 1

    for stt in range(1, 5):
        url = 'https://www.gogoanime1.com/home/latest-episodes/page/' + str(stt)

        req = requests.get(url)
        be = BeautifulSoup(req.content, 'lxml')

        arr_str = be.find_all(class_='dl-item')

        for item in arr_str:
            link = item.find_all('a')[0].get('href')
            link = link.replace('https://www.gogoanime1.com/watch/', '')
            index = link.find('/')
            id_series = link[:index]
            result.append(id_series.strip())

    return result


if __name__ == '__main__':
    stt_id = str(input("Enter id: "))
    # while True:
    #     try:
    # arr_website_avail = get_source_links(stt_id)
    arr_website_avail = get_series()
    print(len(arr_website_avail))
    for id in arr_website_avail:
        black_lists = get_black_lists(stt_id)
        link = get_new_video(id, stt_id, black_lists)

        if link != False:
            check = handle(link['link'], link['eps'], stt_id)

            if check:
                if check == False:
                    print('Waiting next turn')
                    time.sleep(7200)
                else:
                    print('Done!')
                    save_to_file(id, link['eps'], stt_id)
                    time.sleep(100)

        # except:
        #     print("Fail connect!")
