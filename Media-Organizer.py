import os
from shutil import copyfile
from shutil import move

movdst = '/Volumes/ROBS 500GB/Videos/MOV_Files/'
dst = '/Volumes/ROBS 500GB/Videos/'
#rootdir = '/Users/easypawn/Pictures/Photos Library.photoslibrary'
rootdir = '/Volumes/ROBS 500GB/iPhone_Media'
count = 0

for subdir, dirs, files in os.walk(rootdir):
    for file in files:
        path = os.path.join(subdir, file)
        if path.lower().endswith('.mp4'):
            #print("Video found")
            count = count + 1
            newfile = dst + file
            move(path, newfile)
        elif path.lower().endswith('.mov'):
            count = count + 1
            newfile = movdst + file
            move(path, newfile)

print(count)