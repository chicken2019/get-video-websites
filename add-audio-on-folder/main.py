import os
import os.path
from os import path

if __name__ == "__main__":


    thisdir = os.getcwd() + "/input"
    list_file = []

    for r, d, f in os.walk(thisdir):
        list_file = f

    if path.exists("video_concat.ts") is False:
        string = "ffmpeg -loop 1 -i image.jpg -i audio.mp3 -vf \"scale='min(1280,iw)':-2,format=yuv420p\" -c:v libx264 -preset veryslow -profile:v main -c:a aac -shortest -movflags +faststart video_concat.ts"
        os.system(string)

    for file in list_file:
        if path.exists("output/temp.ts"):
            os.remove("output/temp.ts")

        arr = file.split(".")
        arr.pop(len(arr) - 1)
        name = ".".join(arr)

        path_file = thisdir + '/' + file

        string_ts = "ffmpeg -i " + path_file + " -c copy -bsf:v h264_mp4toannexb -f mpegts output/temp.ts"

        os.system(string_ts)

        string_concat = 'ffmpeg -i concat:"output/temp.ts|video_concat.ts" -c copy output/' + name + '.ts'

        os.system(string_concat)

        if path.exists("output/temp.ts"):
            os.remove("output/temp.ts")