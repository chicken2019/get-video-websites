#!/usr/bin/python3
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
from requests.exceptions import ConnectionError

headers_mobile = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B137 Safari/601.1'}
headers_postman = {
    # 'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
    'referer': 'https://www.watchlakorn.in/OMG%E0%B8%9C%E0%B8%B5%E0%B8%9B%E0%B9%88%E0%B8%A7%E0%B8%99%E0%B8%8A%E0%B8%A7%E0%B8%99%E0%B8%A1%E0%B8%B2%E0%B8%A3%E0%B8%B1%E0%B8%81%E0%B8%95%E0%B8%AD%E0%B8%99%E0%B8%97%E0%B8%B5%E0%B9%885%E0%B8%A7%E0%B8%B1%E0%B8%99%E0%B8%97%E0%B8%B5%E0%B9%888%E0%B8%95%E0%B8%B8%E0%B8%A5%E0%B8%B2%E0%B8%84%E0%B8%A12561-video-243982',
    # 'Cache-Control' : 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0',
    # 'Connection' : 'keep-alive',
    # 'Content-Encoding' : 'gzip',
    # 'Content-Length' : '154',
    # 'Content-Type' : 'text/html; charset=TIS-620',
    # 'Keep-Alive' : 'timeout=60',
    # 'Pragma' : 'no-cache',
    # 'Server' : 'nginx',
    # 'Vary' : 'Accept-Encoding',
    # 'X-Powered-By' : 'PHP/5.6.40'
}


def getCodeKt(content):
    video = content.find(id="videoclip")

    if video is None:
        return False
    p = video.find('p')

    if p is None:
        return False

    code_kt = p.get('id')

    return code_kt


def getCodeV(content):
    root = lxml.html.fromstring(content)
    meta = root.xpath("//meta[@property='og:video:url']/@content")
    if len(meta) == 0:
        return False

    meta = meta[0]

    index = meta.rfind('/')

    return meta[index + 1:]


def getPlayList(url, id_series, stt_id):
    headers = {'referer': url}
    re = requests.get(url, headers=headers_mobile)
    content = BeautifulSoup(re.content, 'lxml')

    if content is None:
        return False

    code_kt = getCodeKt(content)
    code_v = getCodeV(re.content)

    if code_v is False or code_kt is False:
        return False

    url2 = "http://www.watchlakorn.in/content_jw6.php?v=" + code_v + "&kt=" + code_kt

    re2 = requests.get(url2, headers=headers)
    content = re2.content

    file = json.loads(content)

    if 'file' not in file[0]:
        return False

    url_play_list = "https:" + (file[0]['file'])
    print(url_play_list)

    if url_play_list.endswith('.mp4') or len(url_play_list) < 10 or 'youtube.com' in url_play_list:
        add_to_black_lists(id_series, stt_id)

        return False

    arr_date = url_play_list.split("/")
    date = arr_date[len(arr_date) - 3]
    date2 = date.split("-")

    if len(date2) < 2:
        return False

    year = date2[2]
    month = date2[1]

    if int(year) < 2019:
        add_to_black_lists(id_series, stt_id)

        return False

    if int(month) < 3:
        return False

    return url_play_list

    re3 = requests.get(url_play_list, headers=headers)
    content = re3.content
    arr = str(content).split('\\n')

    result = []
    for item in arr:
        if '.ts' in item:
            result.append(item)

    return result


def delete_all_video(stt_id):
    pwd = os.getcwd() + '/' + str(stt_id) + '/downloads/'

    filelist = os.listdir(pwd)
    list_file_delete_1 = []
    for fichier in filelist[:]:
        if (fichier.endswith('.ts')):
            list_file_delete_1.append(fichier)

    for file in list_file_delete_1:
        os.remove(pwd + '/' + file)


def get_video(url, file_name):
    path_file = ".ts"
    r = requests.get(url, stream=True)  # create HTTP response object
    with open("downloads\\" + str(file_name) + str(path_file), 'wb') as f:
        for chunk in r.iter_content(chunk_size=2048):
            if chunk:
                f.write(chunk)
    return 'done'


def scale_video():
    os.system('ffmpeg -ss 00:00:50 -y -i "input.mp4"  -i 556330.png -filter_complex "[0:v]eq=brightness=0.05:contrast='
              '0.8:saturation=2:gamma_b=1.0,pad=iw+4:ih+4:2:2:color=white, scale=566:340[v1];movie=xoabg.mp4:loop=999,'
              'setpts=N/(FRAME_RATE*TB), scale = 854:480, setdar =16/9[v2];[v2][v1]overlay=shortest=1:x=-10:y=-10 [v3];'
              '[1:v]scale=854:480 [v4];[v3][v4]overlay=0:0,drawtext=fontfile=fonts/Helvetica-Bold.ttf:text=Please subscr'
              'iber my channel:fontcolor=white:fontsize=36:x=w/10*mod(t\,20):y=400,setdar=16/9;[0:a]aformat=sample_'
              'fmts=fltp:sample_rates=44100:channel_layouts=stereo,atempo=9/10,asetrate=10/9*44100,lowpass=f=3500,high'
              'pass=f=1500,treble=g=16,bass=frequency=110:gain=-50,bass=g=3:f=110:w=1,bass=g=3:f=110:w=2,bass=g=3:f='
              '110:w=3,bass=g=3:f=110:w=4,bass=g=3:f=110:w=5,bass=g=-90,equalizer=f=10.5:width_type=o:width=3:g=-30'
              ', equalizer=f=31.5:width_type=o:width=3:g=-30,equalizer=f=63:width_type=o:width=3:g=-30, equalizer=f='
              '100:width_type=o:width=3:g=-20,equalizer=f=250:width_type=o:width=3:g=-20,equalizer=f=500:width_type='
              'o:width=3:g=-20,equalizer=f=1000:width_type=o:width=3:g=-20,equalizer=f=8000:width_type=o:width=3:g=-3'
              '0,equalizer=f=16000:width_type=o:width=3:g=-30,volume=6,volume=+15dB[a1];[a1]volume=28" -vcodec libx2'
              '64 -pix_fmt yuv420p -r 31 -g 62 -b:v 1800k -shortest -acodec aac -b:a 128k -ar 44100 -metadata album_'
              'artist="" -metadata album="" -metadata date="" -metadata track="" -metadata genre="" -metadata publi'
              'sher="" -metadata encoded_by="" -metadata copyright="" -metadata composer="" -metadata performer="" -m'
              'etadata TIT1="" -metadata TIT3="" -metadata disc="" -metadata TKEY="" -metadata TBPM="" -metadata langu'
              'age="eng" -metadata encoder="" -threads 0 -preset veryfast "output.mp4')

    return "output.mp4"


def get_source_links(stt_id):
    # read file get arr website avail
    fo = open(stt_id + "/source-links.txt", "r")
    arr_website_avail = []
    lines = fo.readlines()

    for line in lines:
        arr_website_avail.append(line.replace('\n', ''))
    fo.close()

    return arr_website_avail


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


def get_new_video(id_series, stt_web):
    url = "https://www.watchlakorn.in/feed/" + str(id_series) + "/rss.xml"
    req = requests.get(url)
    be = BeautifulSoup(req.content, 'lxml')

    arr_str = be.find_all('item')

    if len(arr_str) > 0:
        for item in arr_str:
            string_item = str(item)
            id_video = re.findall(r'video-(.*?) ', string_item)[0]

            if check_exist_chapt(id_series, id_video, stt_web):
                title = item.find('title').string
                title = title.replace(' - WatchLaKorn', '')

                index = title.rfind('-')
                title = title[:index]
                title = title.replace(' 2562', '')

                link = re.findall(r'<link/>(.*?) ', string_item)[0]
                thumbnail = item.find('media:thumbnail').get('url')

                return {
                    'title': title,
                    'link': link,
                    'thumbnail': thumbnail,
                    'id_video': id_video
                }

            break

    return False


def get_description(id_video):
    url = "https://www.watchlakorn.in/feed/" + str(id_video) + "/view.xml"

    req = requests.get(url)
    be = BeautifulSoup(req.content, 'lxml')

    des = be.find("description").string

    return des


def get_string_video(stt_id):
    pwd = os.getcwd() + '/' + str(stt_id) + '/downloads'

    filelist = os.listdir(pwd)
    list_file_delete_1 = []
    for fichier in filelist[:]:
        if (fichier.endswith('.ts')):
            list_file_delete_1.append(fichier)

    string = ''

    list_file_delete_1.sort()

    for file in list_file_delete_1:
        string = string + str(stt_id) + '/downloads/' + str(file) + '|'

    return string[:-1]


def upload_youtube_and_check_out_number(title, description, tags, file_name, thumbnail, stt_id):
    stdout = subprocess.check_output(['youtube-upload', '--title=' + str(title) + '', '--tags="' + str(tags) + '"',
                                      '--description=' + str(description) + '',
                                      '--client-secrets=client_secrets.json',
                                      '--credentials-file=' + str(stt_id) + '/credentials.json', str(file_name)])
    # '--thumbnail=' + thumbnail,
    #
    # arr = ['youtube-upload', '--title="' + str(title) + '"', '--tags=' + tags + '', '--description=' + description + '', '--client-secrets=' + stt_id + '/client_secrets.json', '--credentials-file=' + stt_id + '/credentials.json', file_name]
    # print(arr)
    # result = subprocess.run(arr, stdout=subprocess.PIPE)

    print(stdout)
    return len(stdout) > 0
    # return 'Video URL' in str(result.stdout)


def get_data_file(stt_id, file_name):
    path_file = str(stt_id) + '/' + file_name + '.txt'
    fo = open(path_file, "r")
    lines = fo.readlines()
    fo.close()
    stt_video = ''

    if len(lines) > 0:
        stt_video = lines[0]

    return stt_video


def update_stt_video(stt_id, stt_video):
    path_file = str(stt_id) + '/stt.txt'
    fo = open(path_file, "w")
    fo.write(str(stt_video))
    fo.close()


def isFirstUpload(stt_id):
    f = open(stt_id + '/credentials.json', 'r')
    lines = f.readlines()
    f.close()
    if (len(lines) == 0):
        return True

    return False


def handle(id_series, stt_id):
    arr = get_new_video(id_series, stt_id)

    if arr != False:
        title = str(arr['title'])
        description = str(get_description(arr['id_video']))

        url = arr['link']
        thumbnail = arr['thumbnail']

        start = datetime.datetime.now()
        result = getPlayList(url.encode('utf-8'), id_series, stt_id)

        if result == False or len(result) == 0:
            add_to_black_lists(id_series, stt_id)

            return False

        print("Downloading...")

        os.system(
            "youtube-dl --console-title --hls-prefer-native --hls-use-mpegts -c --no-part --fixup never \"" + result + "\" -o " + str(
                stt_id) + '/temp.mp4')

        string_ts = "ffmpeg -i " + str(stt_id) + '/temp.mp4' + " -c copy -bsf:v h264_mp4toannexb -f mpegts " + str(
            stt_id) + '/input.ts'
        os.system(string_ts)

        file_name = str(stt_id) + '/input.ts'

        file_video = str(stt_id) + "/videos/video_audio.ts"

        string_concat = 'ffmpeg -i concat:"' + file_name + '|' + file_video + '" -c copy ' + str(stt_id) + '/output.ts'

        os.system(string_concat)

        file_name = str(stt_id) + '/output.ts'

        if (isFirstUpload(stt_id)):
            os.system('youtube-upload --title="' + str(
                title) + '" --description="' + description + '" --tags="' + '' + '" ' + '--client-secrets=client_secrets.json --credentials-file=' + str(
                stt_id) + '/credentials.json ' + str(file_name))

            check = True
        else:
            check = upload_youtube_and_check_out_number(title, description, '', str(file_name), thumbnail, stt_id)

        os.remove(str(stt_id) + '/temp.mp4')
        os.remove(str(stt_id) + '/input.ts')
        os.remove(str(stt_id) + '/output.ts')

        if check is False:
            print('Waiting next turn')
            return

        print('Done!')

        save_to_file(id_series, arr['id_video'], stt_id)
        time.sleep(100)

        end = datetime.datetime.now()

        print(end - start)


def add_to_black_lists(id_series, stt_id):
    name_file = str(stt_id) + "/blacklists.txt"

    fo = open(name_file, "a+")
    fo.write(str(id_series) + '\n')
    fo.close()


def main(stt_id, arr_website_avail):
    check = True
    black_lists = get_black_lists(stt_id)

    while check:
        try:
            for id in arr_website_avail:
                if id not in black_lists:
                    try:
                        handle(id, stt_id)
                    except ConnectionError as e:
                        print("buon")

            check = False
        except ConnectionError:
            check = True

    print("Current is: " + str(stt_id))


def convert_ts():
    for i in range(3, 4):
        pwd = os.getcwd() + '/' + str(i) + '/videos'

        filelist = os.listdir(pwd)
        list_file_delete_1 = []
        for fichier in filelist[:]:
            if (fichier.endswith('.mp4')):
                list_file_delete_1.append(fichier)

        stt = 1
        for file in list_file_delete_1:
            item = pwd + '/' + file

            string = "ffmpeg -i '" + item + "' -c copy -bsf:v h264_mp4toannexb -f mpegts " + str(i) + "/videos/" + str(
                stt) + ".ts"

            os.system(string)
            stt += 1


def rename_ts():
    for i in range(3, 4):
        pwd = os.getcwd() + '/' + str(i) + '/videos'

        filelist = os.listdir(pwd)
        list_file = []

        for ficher in filelist[:]:
            if (ficher.endswith('.ts')):
                list_file.append(ficher)

        stt = 1
        for file in list_file:
            item = pwd + '/' + file
            os.rename(item, pwd + '/' + str(stt) + '.ts')
            stt += 1


def download_video_from_url(url):
    headers = {'referer': url}
    re = requests.get(url, headers=headers_mobile)
    content = BeautifulSoup(re.content, 'lxml')

    if content is None:
        return False

    code_kt = getCodeKt(content)
    code_v = getCodeV(re.content)

    if code_v is False or code_kt is False:
        return False

    url2 = "http://www.watchlakorn.in/content_jw6.php?v=" + code_v + "&kt=" + code_kt

    re2 = requests.get(url2, headers=headers)
    content = re2.content

    file = json.loads(content)

    if 'file' not in file[0]:
        return False

    url_play_list = "https:" + (file[0]['file'])
    print(url_play_list)

    arr_date = url_play_list.split("/")
    date = arr_date[len(arr_date) - 3]
    date2 = date.split("-")

    return url_play_list


def get_real_url_video_from_series(id):
    results = []
    url = "https://www.watchlakorn.in/ajax.php?module=load_category&name=load_category&group=" + str(id) + "&category=&searchby=&stype=&searchdate=0&st=0"

    headers = {
        'referer': 'https://www.watchlakorn.in/%E0%B8%81%E0%B8%B5%E0%B8%AC%E0%B8%B2-channel-14'
    }

    req = requests.get(url, headers=headers)
    content = req.content

    id_videos = re.findall(r'div class="vid_thumb"(.*?)</div>', str(content))

    for item in id_videos:
        id = re.findall(r'<a href=\\\'(.*?)\'', str(item))[0]

        results.append(id)

    return results


if __name__ == '__main__':
    # count_stt = str(input("Count: "))
    # id = str(input("Id: "))
    count_stt = 5
    id = 14
    datas = get_real_url_video_from_series(id)

    for item in datas:
        url = "https://www.watchlakorn.in" + item

        url_real = download_video_from_url(url)

        print("Downloading...")

        os.system(
            "youtube-dl --console-title --hls-prefer-native --hls-use-mpegts -c --no-part --fixup never \"" + url_real + "\" -o " + 'temp.mp4')
        break



#"youtube-dl --console-title --hls-prefer-native --hls-use-mpegts -c --no-part --fixup never "https://pl.cdnwatch.com/data10/10-01-2020/OneChampionship-10-Jan-2020.mp4/index.m3u8 -o temp.mp4""