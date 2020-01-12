#!/bin/bash
import os

#string1 = "ffmpeg -loop 1 -i image.jpg -i audio.mp3 -c:v libx264 -tune stillimage -c:a aac -b:a 192k -pix_fmt yuv420p -shortest out.mp4"
#string2 = "ffmpeg -i out.mp4 -c copy -bsf:v h264_mp4toannexb -f mpegts video_audio.ts"
string1 = "ffmpeg -loop 1 -i image.jpg -i audio.mp3 -vf \"scale='min(1280,iw)':-2,format=yuv420p\" -c:v libx264 -preset veryslow -profile:v main -c:a aac -shortest -movflags +faststart output2.mp4"
os.system(string1)
#os.system(string2)

