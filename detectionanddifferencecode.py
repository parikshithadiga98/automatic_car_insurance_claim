#!/usr/bin/env python
# coding: utf-8

# In[1]:


import cv2
import pandas as pd
import numpy as np
from PIL import Image
from PIL import ImageChops
import math
import pymysql
import io

# In[4]:
def sqlconnection():
    db = pymysql.connect("localhost","root","","vehicaldb" )
    conn = db.cursor()
    return conn



def imgreading(cid):
    conn=sqlconnection()
    sql=("""select img1,img2,img3 from images where cusid=%s""",(cid))
    conn.execute(*sql)
    di1,di2,di3=conn.fetchone() 
    sql=("""select timg1,timg2,timg3 from testimg where timgid=%s""",(1))
    conn.execute(*sql)
    tim1,tim2,tim3=conn.fetchone() 
    
    td=pd.read_csv('via_region_data.csv')
    classes=td.region_attributes #reading the csv file of training dataset
    
# In[3]:
    net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg") #yoloapplicationdefaultcode
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))#its not tht important part
    di1=io.BytesIO(di1)
    di2=io.BytesIO(di2)
    di3=io.BytesIO(di3)
    tim1=io.BytesIO(tim1)
    tim2=io.BytesIO(tim2)
    tim3=io.BytesIO(tim3)
    im1=Image.open(di1)
    im2=Image.open(di2)
    im3=Image.open(di3)
    tim1 = Image.open(tim1)
    tim2 = Image.open(tim2)
    tim3 = Image.open(tim3)
    tlist=[tim2,tim1,tim3]
    ti=-1
    rms1=0
    imges=[im1,im2,im3]
    for im in imges:
        ti+=1
        print(im)
        img= cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
   #im1=Image.open("31.jpg") #image for which shd b taken frm db in futher 
    # image for comparing with client image
        img = cv2.resize(img, None, fx=0.6, fy=0.6) #reshaping
        height, width, channels = img.shape 
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False) #blobing the image
        net.setInput(blob) #its the input to the netwrk of yolo
        outs = net.forward(output_layers) #it gives the output  
#detection code
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
            # Object detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
            # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

# In[7]:
    
        diff = ImageChops.difference(tlist[ti], im) #finding the difference of two images
        h = diff.histogram()
        sq = (value*((idx%256)**2) for idx, value in enumerate(h))
        sumofsquares = sum(sq)
        print(sumofsquares)
        rms = math.sqrt(sumofsquares / float(im.size[0] * im.size[1]))
        rms1+=rms
        print(rms1) #rootmeansquare of imagedifference
#code for image display n with damge description
        label1={}
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        #font = cv2.FONT_HERSHEY_PLAIN
        label="yes"
        try:
            for i in range(len(boxes)):
                if i in indexes:
                #x, y, w, h = boxes[i]
                    label1=str(classes[class_ids[i]])
                #print(label1)
                #color = colors[i]
                #cv2.rectangle(img, (x, y), (x + w, y + h), 1, 2)
                #cv2.putText(img, label, (x, y + 30), font, 1,  3)
        except:
            label="not"
    
        
                
    #cv2.imshow("Image", img)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    rms2=rms1/3
    rms=(rms2*100)/rms1
    return label,rms,label1


# In[ ]:





# In[ ]:




