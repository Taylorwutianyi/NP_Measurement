import cv2
import numpy as np
import os
import math
from matplotlib import pyplot as plt

SPHERE_D_MAX = 100
SPHERE_D_MIN = 10
SPHERE_ROUNDNESS = 0.88

CUBE_L_MAX = 100
CUBE_L_MIN = 20
CUBE_SQUARENESS = 0.9

ROD_W_MAX = 50
ROD_W_MIN = 10
ROD_L_MAX = 1000
ROD_L_MIN = 100
ROD_AR_MIN = 3
ROD_AR_MAX = 100
ROD_SQUARENESS = 0.85

IPS_MIN = 0
IPS_MAX = 30
ANGLE_DIFF = 5


IMG_R = 4
LABEL_THICKNESS = 2
FONT = cv2.FONT_HERSHEY_SIMPLEX

def nothing(x):
    pass

def calc_mag(): # calculate the magnification
    sb_list = [100,200,500,1000,2000]
    img_scalebar = []
    img_scalebar.append(cv2.imread(dirpath + "\mag\\100nm.png",0))
    img_scalebar.append(cv2.imread(dirpath + "\mag\\200nm.png",0))
    img_scalebar.append(cv2.imread(dirpath + "\mag\\500nm.png",0))
    img_scalebar.append(cv2.imread(dirpath + "\mag\\1um.png",0))
    img_scalebar.append(cv2.imread(dirpath + "\mag\\2um.png",0))

    img_mag = img[2500:2600,3100:3296] # mag num image
    #cv2.imwrite('2um.png',img_mag)
    score_max = 0
    magi = 0
    for i,sb in enumerate(sb_list):
        res = cv2.matchTemplate(img_mag,img_scalebar[i],cv2.TM_CCOEFF)
        (_,score,_,_) = cv2.minMaxLoc(res)
        if score >= score_max:
            score_max = score
            magi = sb
    img_sb = img[2475:2485,1600:3296] # scale bar image
    ret,img_sb = cv2.threshold(img_sb,50,255,cv2.THRESH_BINARY_INV)
    _,sbcont,_ = cv2.findContours(img_sb,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    mag = float(magi)/(sbcont[0][0][0][0]-sbcont[10][0][0][0])
    return mag

def FindSphere():
    center = (int(x),int(y))
    radius = int(r)
    if w > SPHERE_D_MIN and w < SPHERE_D_MAX \
       and area/(3.14*(w/2)**2) > SPHERE_ROUNDNESS: # standard
        cv2.circle(im,center,radius,(0,255,0),LABEL_THICKNESS)
        cv2.putText(im,str(npn + count),center,FONT,1,(0,255,0),LABEL_THICKNESS,cv2.LINE_AA)
        outline_list.append(((x,y),r))
        return 1
    else:
        return 0
    

def FindCube():
    if w > CUBE_L_MIN and w < CUBE_L_MAX \
       and h/w < 1.1 and area/(w*h) > CUBE_SQUARENESS: # standard
        cv2.drawContours(im, [box], 0, (0,255,0), LABEL_THICKNESS)
        center = (int(rect[0][0]),int(rect[0][1]))
        cv2.putText(im,str(npn + count),center,FONT,1,(0,255,0),LABEL_THICKNESS,cv2.LINE_AA)
        outline_list.append(rect)
        return 1
    else:
        return 0

def FindRod():
    if w > ROD_W_MIN and w < ROD_W_MAX and h > ROD_L_MIN and h < ROD_L_MAX and \
       h/w > ROD_AR_MIN and h/w < ROD_AR_MAX and area/(w*h) > ROD_SQUARENESS: # standard
        cv2.drawContours(im, [box], 0, (0,255,0), LABEL_THICKNESS)
        center = (int(rect[0][0]),int(rect[0][1]))
        cv2.putText(im,str(npn + count),center,FONT,1,(0,255,0),LABEL_THICKNESS,cv2.LINE_AA)
        outline_list.append(rect)
        return 1
    else:
        return 0

def enlarge(event,x,y,flags,param): # inset image position
    global ix,iy,captureflag,x1,x2,y1,y2

    if event == cv2.EVENT_LBUTTONDOWN:
        captureflag = True
        ix,iy = x,y

    elif event == cv2.EVENT_MOUSEMOVE:
        if captureflag == True:
            x1 = min(ix,x)
            x2 = max(ix,x)
            y1 = min(iy,y)
            y2 = max(iy,y)

    elif event == cv2.EVENT_LBUTTONUP:
        captureflag = False

def ExportIps(): # export ips measurements
    ips_file = open(dirpath + '\\' + foldername + '\\results\\ips.txt','w')
    if npipspairs == 0:
        print ('No measurements!')
        ips_file.write('No measurements! \n')
        return
    ips_file.write("AVG_ips=%s \n\n" % (str(npips/npipspairs)))
    ips_file.write("Index Pair ips \n")
    for i,item in enumerate(ips_all):
        ips_file.write("%s %s %s \n" % (i,item[0],item[1]))
    ips_file.close()

def IpsSphere():
    ips = ipspairs = 0
    for i in range(count):
        x1 = outline_list[i][0][0]
        y1 = outline_list[i][0][1]
        r1 = outline_list[i][1]
        for j in range(i + 1,count):
            x2 = outline_list[j][0][0]
            y2 = outline_list[j][0][1]
            r2 = outline_list[j][1]
            dist = mag*(((x1 - x2)**2 + (y1 - y2)**2)**0.5 - r1 - r2)
            if dist < IPS_MAX and dist > IPS_MIN:
                theta = np.arctan2((y2 - y1),(x2 - x1))
                a = (int(x1 + r1*math.cos(theta)),int(y1 + r1*math.sin(theta)))
                b = (int(x2 - r2*math.cos(theta)),int(y2 - r2*math.sin(theta)))
                cv2.line(im,a,b,(255,0,0),LABEL_THICKNESS)
                ips_temp.append(((npn + i,npn + j),dist))
                ipspairs += 1
                ips += dist
    return ips,ipspairs
 

def IpsCube():
    ips = ipspairs = 0
    for i in range(count):
        x1 = outline_list[i][0][0]
        y1 = -outline_list[i][0][1]
        theta1 = -outline_list[i][2]
        k = math.tan(theta1*math.pi/180)
        b1 = y1 - k*x1 # kx - y + b1 = 0
        l1 = (outline_list[i][1][0] + outline_list[i][1][1])/2
        for j in range(i + 1,count):
            x2 = outline_list[j][0][0]
            y2 = -outline_list[j][0][1]
            theta2 = -outline_list[j][2]
            if abs(theta1 - theta2) < ANGLE_DIFF:
                b2 = y2 - k*x2 # kx - y + b2 = 0
                l2 = (outline_list[j][1][0] + outline_list[j][1][1])/2
                d1 = abs(b1 - b2)*math.cos(theta1*math.pi/180) # distance between positive slope lines
                d2 = ((x1 - x2)**2 + (y1 - y2)**2 - d1**2)**0.5 # distance between negative slope lines
                dist1 = mag*(d1 - l1/2 - l2/2)
                dist2 = mag*(d2 - l1/2 - l2/2)
                if dist1 < IPS_MAX and  dist1 > IPS_MIN and dist2 < -l2/2*mag:
                    ips_temp.append(((npn + i,npn + j),dist1))
                    ipspairs += 1
                    ips += dist1
                    (a,b) = GetPoints(k,theta1,b1,b2,l1,dist1/mag,x1,-y1)
                    cv2.line(im,a,b,(255,0,0),LABEL_THICKNESS)
                elif dist2 < IPS_MAX and dist2 > IPS_MIN and dist1 < -l2/2*mag:
                    ips_temp.append(((npn + i,npn + j),dist2))
                    ipspairs += 1
                    ips += dist2
                    if k == 0:
                        k_2 = 'YouF*ckedUp'
                        b_1 = x1
                        b_2 = x2
                    else:
                        k_2 = -1/k
                        b_1 = y1 - k_2*x1
                        b_2 = y2 - k_2*x2
                    (a,b) = GetPoints(k_2,theta1,b_1,b_2,l1,dist2/mag,x1,-y1)
                    cv2.line(im,a,b,(255,0,0),LABEL_THICKNESS)
    return ips,ipspairs

def IpsRod():
    ips = ipspairs = 0
    for i in range(count):
        x1 = outline_list[i][0][0]
        y1 = -outline_list[i][0][1]
        theta1 = -outline_list[i][2]
        k = math.tan(theta1*math.pi/180)
        b1 = y1 - k*x1 # kx - y + b1 = 0, k = tan(theta)
        l11 = outline_list[i][1][0]
        l12 = outline_list[i][1][1]
        for j in range(i + 1,count):
            x2 = outline_list[j][0][0]
            y2 = -outline_list[j][0][1]
            theta2 = -outline_list[j][2]
            if abs(theta1 - theta2) < ANGLE_DIFF: # angle difference
                b2 = y2 - k*x2 # kx - y + b2 = 0
                l21 = outline_list[j][1][0]
                l22 = outline_list[j][1][1]
                d1 = abs(b1 - b2)*math.cos(theta1*math.pi/180) # distance between positive slope lines
                d2 = ((x1 - x2)**2 + (y1 - y2)**2 - d1**2)**0.5 # distance between negative slope lines
                if l11 < l12 and l21 < l22: # rods pointing to NW
                    dist1 = mag*(d1 - l12/2 - l22/2)
                    dist2 = mag*(d2 - l11/2 - l21/2)
                    if dist2 < IPS_MAX and  dist2 > IPS_MIN and dist1 < -l22/2*mag:
                        ips_temp.append(((npn + i,npn + j),dist2))
                        ipspairs += 1
                        ips += dist2
                        if k == 0:
                            k_2 = 'YouF*ckedUp'
                            b_1 = x1
                            b_2 = x2
                        else:
                            k_2 = -1/k
                            b_1 = y1 - k_2*x1
                            b_2 = y2 - k_2*x2
                        (a,b) = GetPoints(k_2,theta1,b_1,b_2,l11,dist2/mag,x1,-y1)
                        cv2.line(im,a,b,(255,0,0),LABEL_THICKNESS)
                if l11 > l12 and l21 > l22: # rods pointing to NE
                    dist1 = mag*(d1 - l12/2 - l22/2)
                    dist2 = mag*(d2 - l11/2 - l21/2)
                    if dist1 < IPS_MAX and  dist1 > IPS_MIN and dist2 < -l21/2*mag:
                        ips_temp.append(((npn + i,npn + j),dist1))
                        ipspairs += 1
                        ips += dist1
                        (a,b) = GetPoints(k,theta1,b1,b2,l12,dist1/mag,x1,-y1)
                        cv2.line(im,a,b,(255,0,0),LABEL_THICKNESS)
                        #draw
    return ips,ipspairs

def GetPoints(k,theta,b1,b2,w,d,x,y):
# k: slope of long axis; theta: angle
# b1: intercept of i; b2: intercept of j;
# w: width of i; d: ips
# x,y: center of i
    if k == 'YouF*ckedUp':
        if b1 < b2:
            xa = x + w/2
            ya = y
            xb = x + w/2 + d
            yb = y
        else:
            xa = x - w/2
            ya = y
            xb = x - w/2 - d
            yb = y
    elif k >= 0:
        if b1 > b2:
            xa = x + w/2*math.sin(theta*math.pi/180)
            ya = y + w/2*math.cos(theta*math.pi/180)
            xb = x + (w/2 + d)*math.sin(theta*math.pi/180)
            yb = y + (w/2 + d)*math.cos(theta*math.pi/180)
        else:
            xa = x - w/2*math.sin(theta*math.pi/180)
            ya = y - w/2*math.cos(theta*math.pi/180)
            xb = x - (w/2 + d)*math.sin(theta*math.pi/180)
            yb = y - (w/2 + d)*math.cos(theta*math.pi/180)
    else:
        if b1 > b2:
            xa = x - w/2*math.cos(theta*math.pi/180)
            ya = y + w/2*math.sin(theta*math.pi/180)
            xb = x - (w/2 + d)*math.cos(theta*math.pi/180)
            yb = y + (w/2 + d)*math.sin(theta*math.pi/180)
        else:
            xa = x + w/2*math.cos(theta*math.pi/180)
            ya = y - w/2*math.sin(theta*math.pi/180)
            xb = x + (w/2 + d)*math.cos(theta*math.pi/180)
            yb = y - (w/2 + d)*math.sin(theta*math.pi/180)
    
    return (int(xa),int(ya)),(int(xb),int(yb))
        

dirpath = os.getcwd()
nptype = -1 #nanoparticle type

for foldername in os.listdir(dirpath):
    if foldername.startswith('sphere'):
        nptype = 0 
    elif foldername.startswith('cube'):
        nptype = 1
    elif foldername.startswith('rod'):
        nptype = 2
    else:
        continue
    ips_all = []
    npips = 0
    npipspairs = 0
    npn = 0
    captureflag = False
    if os.path.isdir(foldername + '\\results') == False:
        os.mkdir(foldername + '\\results')
    for filename in os.listdir(dirpath + '\\' + foldername):
        if filename.endswith('.jpg') or filename.endswith('.tif'):
            img0 = cv2.imread(dirpath + '\\' + foldername + '\\' + filename)
            img = cv2.cvtColor(img0,cv2.COLOR_BGR2GRAY)
            x1 = y1 = 0
            x2 = y2 = 1
            r,c = img.shape # 2788 * 3296
            r2 = int(r/IMG_R)
            c2 = int(c/IMG_R)
            mag = calc_mag()
            #img_blur = cv2.GaussianBlur(img,(5,5),0)
            img_blur = cv2.medianBlur(img[0:2450,0:3296],5)
            
            #plt.hist(img_blur.ravel(),256,(0,255))
            #plt.show()

            cv2.namedWindow('dst')
            cv2.createTrackbar('Thresh','dst',50,100,nothing)
            cv2.setMouseCallback('dst',enlarge)
            threshflag = -1
            while(True):
                thresh = cv2.getTrackbarPos('Thresh','dst')
                if thresh != threshflag:
                    otsu,img_bw = cv2.threshold(img_blur,thresh,255,cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                    ret,img_bw = cv2.threshold(img_blur,otsu - 60 + thresh,255,cv2.THRESH_BINARY_INV)
                    #print (otsu)
                    _,cont,_= cv2.findContours(img_bw,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                    im = np.copy(img0)
                    count = 0
                    outline_list = []
                    ips_temp = []
                    ips = ipspairs = 0
                    for conti in cont:
                        #cv2.drawContours(im, [conti], 0, (0,0,255), 2)
                        rect = cv2.minAreaRect(conti)
                        area = cv2.contourArea(conti)*mag**2
                        box = np.int0(cv2.boxPoints(rect))
                        w = min(rect[1])*mag
                        h = max(rect[1])*mag
                        isnp = 0
                        if nptype == 0:
                            (x,y),r = cv2.minEnclosingCircle(conti)
                            h = w = 2*r*mag
                            isnp = FindSphere()
                        elif nptype == 1:
                            isnp = FindCube()
                        elif nptype == 2:
                            isnp = FindRod()
                        if isnp == 1:
                            count += 1
                    if count > 0:
                        if nptype == 0:
                            ips,ipspairs = IpsSphere()
                        elif nptype == 1:
                            ips,ipspairs = IpsCube()
                        elif nptype == 2:
                            ips,ipspairs = IpsRod()
                        #print ('pairs=' + str(ipspairs) + '\n')
                    threshflag = thresh
                im_resize = cv2.resize(im,(c2,r2),interpolation = cv2.INTER_AREA)
                cv2.rectangle(im_resize,(x1,y1),(x2,y2),(0,0,255),1)
                cv2.imshow('dst',im_resize)
                if captureflag == False and y1 - y2 != 0 and x1 - x2 != 0:
                    im_inset = im[y1*IMG_R:y2*IMG_R,x1*IMG_R:x2*IMG_R]
                    cv2.imshow('inset',im_inset)
                k = cv2.waitKey(10) & 0xFF
                if k == ord('n'):
                    ips_all.extend(ips_temp)
                    cv2.imwrite(dirpath + '\\' + foldername + '\\results\\' + \
                                    os.path.splitext(filename)[0] + '_labelled_ips.jpg',im)
                    npn += count
                    npips += ips
                    npipspairs += ipspairs
                    if npipspairs == 0:
                        break
                    else:
                        print ('Until now:')
                        print ('pairs=' + str(npipspairs) + '\nips=' + str(npips/npipspairs) + '\n')
                        
                    cv2.destroyAllWindows()
                    break
                elif k == 27:
                    cv2.destroyAllWindows()
                    exit()
    ExportIps()

cv2.destroyAllWindows()
cv2.waitKey(0)
