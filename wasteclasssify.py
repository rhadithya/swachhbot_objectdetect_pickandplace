#same as objvid2, modular
import cv2
import numpy as np
import time 
import urllib2
import sys
import paho.mqtt.client as mqtt
#from msvcrt import getch
#from matplotlib import pyplot as plt

#minimum match count for classifier
MIN_MATCH_COUNT = 10

RESIZE_PARAM=500.0
font = cv2.FONT_HERSHEY_SIMPLEX #use this for opencv3 onwards
#font= cv2.CV_FONT_HERSHEY_SIMPLEX

cascade1 = cv2.CascadeClassifier('trash1.xml')
cascade2 = cv2.CascadeClassifier('recycle1.xml')


#the function is used to resize the video frames to a standard value described by RESIZE_PARAM
def objresize(img,RESIZE_PARAM):
    r = RESIZE_PARAM / img.shape[1]
    dim = (int(RESIZE_PARAM), int(img.shape[0] * r))
    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    return img

def objdetect(det,imgg1,imgg2):
    #det to be initialised by any methods outside the infinite while as
    #sift = cv2.SIFT()
    #sift = cv2.xfeatures2d.SIFT_create()
    #surf=cv2.xfeatures2d.SURF_create()
    # find the keypoints and descriptors for the keypoints with SIFT(or SURF)
    keypts1, descriptor1 = det.detectAndCompute(imgg1,None)
    keypts2, descriptor2 = det.detectAndCompute(imgg2,None)

    #better faster implementation of knn classifier
    #FLANN_INDEX_KDTREE = 0
    #index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
    #search_params = dict(checks = 50)
    matcher=cv2.BFMatcher()
     #flann = cv2.FlannBasedMatcher(index_params, search_params)
    matches = matcher.knnMatch(descriptor1,descriptor2,k=2)
    #matches=flann.knnMatch(np.asarray(descriptor1,np.float32),np.asarray(descriptor2,np.float32), 2)

    # store all the good matches as per Lowe's ratio test.
    #matches contains 2 lists, of approximate distance to two classes since k=2
    # consider having more difference in distance between two classes
    good = []
    for m,n in matches:
        if m.distance < 0.7*n.distance:
            good.append(m)
    center=0.0
    dst=0
    #only if sufficient number of matches are found then continue
    if len(good)>MIN_MATCH_COUNT:
        dst_pts = np.float32([ keypts1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)#src and dst interchanged
        src_pts = np.float32([ keypts2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)

         #using source and destination points find perspective transformation function
        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)

        if mask is not None:
            matchesMask = mask.ravel().tolist()

            h,w = imgg2.shape
            pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
            #apply the transformation function for required source points to
            #obtain its location in destination image
            #ie applying the 3by3 transformation mask at corners of source image
            #to obtain its position in destination image 
            dst = cv2.perspectiveTransform(pts,M)
            #print((dst[0]+dst[1]+dst[2]+dst[3])/4)
            #print(dst[3])
            center=(dst[0]+dst[1]+dst[2]+dst[3])/4
            #the origin O(0,0) is taken as centre of the frame 
            #the first parameter is the error in x direction,
            #large negative value implies object is to the left of origin, large positive implies object is in right of origin proportionately
            #the second parameter is the error in y direction,
            #large negative value implies object is above the origin and large positive implies object is below the origin proportionately
            error=center-[250.0, 187.0]
            #error is numpy ndarray
            #error in x direction
            errorX=error.item(0)
            #error in y direction
            errorY=error.item(1)
            #print(error)
            error_string=str(int(errorX))+" "+str(int(errorY))
            #the error_string is published in the mqtt server topic errorvals
            mqttc.publish(topic='errorvals',payload=error_string, qos=0)
            print(error_string)
            #imgg1 = cv2.polylines(imgg1,[np.int32(dst)],True,255,3, cv2.LINE_AA)
            cv2.polylines(imgg1,[np.int32(dst)],True,255,3)#cv2.CV_AA
        else:
            print('mask is none')
    else:
        print ("Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT))
        matchesMask = None

        
    cv2.imshow('video',imgg1)
    return center
'''
    draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                singlePointColor = None,
                matchesMask = matchesMask, # draw only inliers
                flags = 2)
        #print the below image to show corresponding points and transformations 
    img3 = cv2.drawMatches(imgg1,keypts1,imgg2,keypts2,good,None,**draw_params)

    #plt.imshow(img3, 'gray'),plt.show()
    cv2.imshow('video',imgg1)
'''        
   # return center

'''
def objdraw(matchesMask,img1,img2,keypts1,keypts2):
    draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                singlePointColor = None,
                matchesMask = matchesMask, # draw only inliers
                flags = 2)
    #print the below image to show corresponding points and transformations 
    img3 = cv2.drawMatches(img1,keypts1,img2,keypts2,good,None,**draw_params)

    #plt.imshow(img2, 'gray'),plt.show()
    cv2.imshow('img3',img3)
'''    
#########################################################################




cap=cv2.VideoCapture(0)
#time.sleep(2)
cap.set(3, 480)
cap.set(4, 240)

counter=0

while(1):
    e1 = cv2.getTickCount()
    _,img1=cap.read()
    img1=objresize(img1,RESIZE_PARAM)
    gray=cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)


    ##############################################
    objects1 =cascade1.detectMultiScale(gray, 1.1,12) #(1.1,5)
    for (x,y,w,h) in objects1:
        cv2.rectangle(img1,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img1[y:y+h, x:x+w]
        midX=x+w/2
        midY=y+h/2
        cv2.putText(img1,'trash',(20,20), font, 0.5, (255,255,255), 1, cv2.CV_AA)
        cv2.putText(img1,'x:'+ str(midX),(20,40), font, 0.5, (255,255,255), 1, cv2.CV_AA)
        cv2.putText(img1,'y:'+ str(midY),(20,60), font, 0.5, (255,255,255), 1, cv2.CV_AA)

        errorX=midX-250.0
        errorY=midY-187.0
        #error_string=str("object1 "+ int(errorX))+" "+str(int(errorY))
        error_string="trash "+str(errorX)+" "+str(errorY)
        print(error_string)
        

    objects2 =cascade2.detectMultiScale(gray, 1.1,12)
    for (a,b,c,d) in objects2:
        cv2.rectangle(img1,(a,b),(a+c,b+d),(0,0,255),2)
        roi_gray = gray[b:b+d, a:a+c]
        roi_color = img1[b:b+d, a:a+c]
        midX=a+c/2
        midY=b+d/2
        cv2.putText(img1,'recycle',(20,20), font, 0.5, (255,255,255), 1, cv2.CV_AA)
        cv2.putText(img1,'x:'+ str(midX),(20,40), font, 0.5, (255,255,255), 1, cv2.CV_AA)
        cv2.putText(img1,'y:'+ str(midY),(20,60), font, 0.5, (255,255,255), 1, cv2.CV_AA)

        errorX=midX-250.0
        errorY=midY-187.0
        #error_string=str("object1 "+ int(errorX))+" "+str(int(errorY))
        error_string="recycle "+str(errorX)+" "+str(errorY)
        print(error_string)

                                                          
    ###############################################
    #display the final image
    #common for all cascades
    #cv2.putText(img1,'matchbox',(10,500), font, 4,(255,0,0),2)
    
   
    cv2.imshow('img1',img1)

    ###############################################
    #print(point)
    '''
    key = ord(getch())
    if key == 27: #ESC
        print("enter key hit")
    '''
    
    k=cv2.waitKey(5) & 0xFF
    if k==27:
        break
    e2 = cv2.getTickCount()
    t = (e2 - e1)/cv2.getTickFrequency()
    #print t 

cv2.waitKey(0)                 
cv2.destroyAllWindows() 
cv2.waitKey(1)
cv2.waitKey(1)
cv2.waitKey(1)
cv2.waitKey(1)  



            
