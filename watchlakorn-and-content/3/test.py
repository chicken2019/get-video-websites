from moviepy.editor import VideoFileClip, concatenate_videoclips
clip1 = VideoFileClip("temp.mp4")
clip2 = VideoFileClip("input2.mp4")
final_clip = concatenate_videoclips([clip1,clip2])

final_clip.write_videofile("my_concatenation.mp4")
