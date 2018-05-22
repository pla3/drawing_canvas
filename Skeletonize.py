#!/usr/bin/env python
#! -*- coding: utf-8 -*-

from skimage.morphology import skeletonize
import numpy as np
import cv2
from line_segmentation import *
from line_simplification import *

img = cv2.imread('testImg_mikuface.png', -1)
img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
img = cv2.bitwise_not(img)

# perform skeletonization
skeleton = skeletonize(img / 255) #0-255 -> 0-1
img_thin = skeleton.astype(np.uint8) * 255

# display results
h, w = img_thin.shape[:2]
dstPts = divideBranchedChain(img_thin.ravel(), w, h, False)
img_dst = np.zeros((h, w, 3), dtype=np.uint8)
for i, pts in enumerate(dstPts):
    color = [0, 0, 0]
    color[i%3] = 255
    if len(pts) > 12:
        #for p in pts:
        #    cv2.circle(img_dst, p, 0, color)
        simplified = ramerdouglas(pts, dist=1.4)
        p0 = simplified[0]
        for i in range(1, len(simplified)):
            p1 = simplified[i]
            cv2.line(img_dst, p0, p1, color)
            p0 = p1
        for p in simplified:
            cv2.circle(img_dst, p, 1, (255, 255, 255))

cv2.imshow('src image', img)
cv2.imshow('thin image', img_thin)
cv2.imshow('dst image', img_dst)
cv2.waitKey(0)
cv2.destroyAllWindows()
'''
'''
