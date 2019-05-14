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
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options


def get_video(url, file_name, stt_id):
    path_file = ".mp4"
    r = requests.get(url, stream=True)  # create HTTP response object
    with open(str(stt_id) + "\\downloads\\" + str(file_name) + str(path_file), 'wb') as f:
        for chunk in r.iter_content(chunk_size=2048):
            if chunk:
                f.write(chunk)

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
                    fo.close()
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

        lines.append(str(id_series) + ':' + str(id_chapt_new))
    fo.close()

    fo = open(name_file, "w")
    fo.writelines(lines)
    fo.close()
    return True


def download_video_by_youtube_dl(url, stt_id):
    cmd = "youtube-dl -o " + str(stt_id) + "/downloads/input.%(ext)s " + str(url)
    os.system(cmd)

    return True


def get_link_by_selenium(url):
    chrome_options = Options()
    chrome_options.set_headless(True)
    driver = webdriver.Chrome('C:\chromedriver_win32\chromedriver.exe', chrome_options=chrome_options)

    driver.get(url)
    driver.implicitly_wait(3)

    html1 = driver.page_source
    soup = BeautifulSoup(html1, 'lxml')

    iframe = soup.find_all("iframe")

    url2 = iframe[0].get('src')
    print(url2)
    driver.get(url2)

    html2 = driver.page_source
    root = html.fromstring(html2)
    video = root.xpath("//video/source/@src")
    length = len(video)
    source = video[length - 1]

    driver.close()
    driver.quit()

    return source


def handle(url, id_series, stt_id):
    start = datetime.datetime.now()
    print("Finding link...")

    arr_1 = get_url_1(url)
    arr_2 = get_data_id(arr_1['url'])

    eps = int(arr_2['ep'])
    check = check_exist_chapt(id_series, eps, stt_id)

    if check is False:
        return True

    # url2 = "https://www6.fmovies.to/ajax/episode/info?ts=" + str(arr_1['data_ts']) + "&id=" + str(arr_2['data_id']) + "&server=33"
    # url3 = get_url_2(url2, url, arr_2['data_path'])

    # link_video = get_url_3(url3, url, arr_2['data_path'])
    link_video = get_link_by_selenium(url + '/' + arr_2['data_path'])

    print(link_video)
    print("Downloading video...")

    check = get_video(link_video, 'input', stt_id)
    # check = download_video_by_youtube_dl(link_video, stt_id)

    if check:
        title = arr_1['title'] + " eps " + str(eps)
        description = arr_1['des']
        genres = arr_1['genres']

        print("Processing...")

        os.system('ffmpeg -noaccurate_seek -ss 00:12:00 -i '
                  + str(stt_id) + '\\downloads\\input.mp4 -to 00:02:50 -c copy '
                  + str(stt_id) + '\\downloads\\output.mp4')

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

        return eps

    return check


def get_url_1(url):
    index_code = url.rfind('.')
    code = url[index_code + 1:]
    req = requests.get(url)
    root = html.fromstring(req.content)

    data_ts = root.xpath('//html/@data-ts')[0]

    title = root.xpath('//*[@id="info"]/div/div[2]/div/h1/text()')[0]
    thumbnail_url = root.xpath('//*[@id="info"]/div/div[1]/img/@src')[0]
    des = root.xpath('//*[@id="info"]/div/div[2]/div/div[3]/text()')[0]
    genres = root.xpath('//*[@id="info"]/div/div[2]/div/div[4]/dl[1]/dd[1]/a/text()')
    genres = ','.join(genres)

    return {
        'data_ts': data_ts,
        'url': 'https://www6.fmovies.to/ajax/film/servers/' + code + '?ts=' + data_ts,
        'title': title,
        'thumbnail_url': thumbnail_url,
        'des': des,
        'genres': genres
    }


def get_data_id(url):
    req = requests.get(url)
    content = req.content

    html1 = json.loads(content)
    html1 = html1['html']

    be = BeautifulSoup(html1, 'lxml')
    server = be.find_all('ul')[2]
    arr_a = server.find_all('a')
    a = arr_a[len(arr_a) - 1]
    data_id = a.get('data-id')
    data_path = a.get('href')
    index = data_path.rfind('/')
    data_path = data_path[index + 1:]
    ep = a.string

    return {'data_id': data_id, 'data_path': data_path, 'ep': ep}


def get_url_2(url, url_film, data_path):
    data = {
        'referer': url_film + '/' + data_path,
    }

    for i in range(1200, 1300):
        url = url + "&_=" + str(i)

        req = requests.get(url, headers=data)

        content = str(req.content)
        if "error" not in content:
            txt = content.replace("\\\\", "")
            arr = re.findall(r"\"target\":\"(.*?)\"", txt)

            return arr[0]


def get_url_3(url, url_film, data_path):
    print(url)
    data = {
        'referer': url_film + '/' + data_path,
    }
    print(data)
    req = requests.get(url, headers=data)
    print(req.content)
    root = html.fromstring(req.content)
    video = root.xpath("//video/source/@src")
    length = len(video)
    source = video[length - 1]

    return source


def isFirstUpload(stt_id):
    f = open(stt_id + '/credentials.json', 'r')
    lines = f.readlines()
    f.close()
    if(len(lines) == 0):
        return True

    return False


def get_black_lists():
    results = []
    name_file = "blacklists.txt"

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


def get_series():
    result = []

    for stt in range(1, 3):
        url = 'https://www6.fmovies.to/tv-series?page=' + str(stt)

        req = requests.get(url)
        be = BeautifulSoup(req.content, 'lxml')

        arr_str = be.find(class_='row movie-list').find_all(class_="name")

        for item in arr_str:
            link = item.get('href')
            index = link.rfind('/')
            link = link[index + 1:]
            result.append(link)

    return result


if __name__ == '__main__':
    stt_id = str(input("Enter id: "))

    while True:
        try:
            # arr_website_avail = get_source_links(stt_id)
            arr_website_avail = get_series()

            for id in arr_website_avail:
                black_lists = get_black_lists()
                check_1 = id not in black_lists

                if check_1 is True:
                    url = "https://www6.fmovies.to/film/" + id
                    print(url)
                    eps = handle(url, id, stt_id)

                    if eps is True:
                        continue

                    if eps != False:
                        print('Done!')
                        save_to_file(id, int(eps), stt_id)
                        time.sleep(100)
                    else:
                        print('Waiting next turn')
                        time.sleep(7200)

        except:
            print("Error!")