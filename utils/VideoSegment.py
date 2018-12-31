# coding: utf-8
import cv2
import os
import random
import shutil
from skimage.measure import compare_ssim


def image_selector(ImagePath, TargetPath) :
    count = 0
    for label in os.listdir(ImagePath):
        file_dir = os.path.join(ImagePath, label)
        file_list = os.listdir(file_dir)

        rand = random.randrange(0, len(file_list)-1)
        file_path = os.path.join(file_dir, file_list[rand])
        shutil.copy(file_path, TargetPath)
        count +=1
 
    return count


def image_reader(pathIn, pathOut, ImagePath):
    image_name_list = [f for f in os.listdir(ImagePath)]
    # print(image_name_list)
    image_list= []
    filename_list = []
    for i in range(len(image_name_list)):
        print(ImagePath + image_name_list[i])
        img = cv2.imread(ImagePath + image_name_list[i])
        image_list.append(img)
    #convert every image's color into gray
    for i in range(len(image_list)):
        image_list[i] = cv2.cvtColor(image_list[i], cv2.COLOR_BGR2GRAY)
    #image_list holds images to compare with video's capturing image
    count = 0
    vidcap = cv2.VideoCapture(pathIn)
    success, image = vidcap.read()
    
    while success :
        vidcap.set(cv2.CAP_PROP_POS_MSEC,(count*500)) #based on 1 second interval
        success,image = vidcap.read()
        if success:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # print ('Read a new frame: ', success)
            # print('testing comparison score')
            score_list = []
            diff_list = []
            for i in range(len(image_list)):
                size = (gray_image.shape[1], gray_image.shape[0])
                image_list[i] = cv2.resize(image_list[i], size)
                (score, diff) = compare_ssim(gray_image, image_list[i], full=True)
                # print('comparing with ', i, ' score : ', score, ', diff : ', diff)
                score_list.append(score)
                diff_list.append(diff)
            print('max score', max(score_list))
            if(max(score_list) > 0.3): # 0.3 
                cv2.imwrite( pathOut + "/frame_%d.jpg" % count, image)     # save frame as JPEG file
                filename_list.append(pathOut + "/frame_%d.jpg" %count)
            count = count + 1
    vidcap.release()
    return filename_list


