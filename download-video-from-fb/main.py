import requests
import json
import time
import os
import subprocess
from random import randrange

def get_video(url, file_name):
    r = requests.get(url, stream=True)  # create HTTP response object
    with open(str(file_name), 'wb') as f:
        for chunk in r.iter_content(chunk_size=2048):
            if chunk:
                f.write(chunk)

    return file_name


def convert_time(minutes):
    return time.strftime('%H:%M:%S', time.gmtime(minutes))


def splitVideo(file_name, length_video, time_need):
    stt_from = 0
    stt = 1
    is_break = False

    while True:
        from_time = convert_time(stt_from)
        to_time = convert_time(time_need)

        if stt_from + time_need >= length_video:
            to_time = convert_time(time_need + length_video - stt_from)
            is_break = True

        string = 'ffmpeg -noaccurate_seek -ss ' + from_time + ' -i ' + file_name + ' -to ' + to_time + ' -c copy input/input' + str(stt) + '.mp4'
        print(string)
        os.system(string)

        if is_break:
            return stt

        stt_from = stt_from + time_need + 1
        stt = stt + 1


def get_data_file(file_name):
    path_file = file_name
    fo = open(path_file, "r")
    lines = fo.readlines()
    fo.close()
    stt_video = ''

    if len(lines) > 0:
        stt_video = lines[0]

    return stt_video


def getLengthVideo(input_video):
    string = 'ffprobe -i ' + input_video + ' -show_entries format=duration -v quiet -of csv="p=0"'

    result = subprocess.getoutput(string)

    return round(float(result), 0)


def getSourceVideo(id):
    access_token = get_data_file("access_token.txt")
    url = "https://graph.facebook.com/v3.3/" + str(id) + "?fields=source&access_token=" + access_token
    req = requests.get(url)

    datas = json.loads(req.content)
    return datas['source']


def getSourceVideoByPage(id):
    access_token = get_data_file("access_token.txt")
    url = "https://graph.facebook.com/v3.3/" + str(id) + "/videos?fields=source&access_token=" + access_token
    req = requests.get(url)

    datas = json.loads(req.content)

    return datas['data']



def rename_ts():
    for i in range(3, 4):
        pwd = os.getcwd() + '/input'

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


def convert_ts():
    for i in range(3, 4):
        pwd = os.getcwd() + '/input'

        filelist = os.listdir(pwd)
        list_file_delete_1 = []
        for fichier in filelist[:]:
            if (fichier.endswith('.mp4')):
                list_file_delete_1.append(fichier)

        stt = randrange(0, 1000, 2)

        for file in list_file_delete_1:
            item = pwd + '/' + file

            string = "ffmpeg -i " + item + " -c copy -bsf:v h264_mp4toannexb -f mpegts input/" + str(stt) + ".ts"

            os.system(string)
            stt = randrange(0, 1000, 2)


if __name__ == '__main__':
    # ffprobe -i ' + input_video + ' -show_entries format=duration -v quiet -of csv="p=0"

    option = str(input("Find by id(0) - page(1) ? "))

    if option == "1":
        i = 0
        id = str(input("Id page: "))
        sources = getSourceVideoByPage(id)

        if len(sources) > 0:
            print("Downloading video...")

            for i in range(len(sources)):
                source = sources[i]["source"]
                file_name = get_video(source, 'input/input' + str(i + 1) + '.mp4')

    else:
        id = str(input("Id: "))
        source = getSourceVideo(id)

        print("Downloading video...")
        file_name = get_video(source, 'input.mp4')
        file_name = 'input.mp4'
        length_video = getLengthVideo(file_name)

        splitVideo(file_name, length_video, 400)

    convert_ts()
    os.system("rm -rf input.mp4")
    os.system("rm -rf input/*.mp4")

    option = str(input("Rename ? "))

    if option == "1":
        rename_ts()
