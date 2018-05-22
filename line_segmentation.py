#!/usr/bin/env python
#! -*- coding: utf-8 -*-

# original code by @TatsuyaOGth
# https://qiita.com/TatsuyaOGth/items/292317e9f5a5256098e7

import cv2
import numpy as np

# Output data type
#Point2dArray # typedef std::vector<std::array<int, 2> >

'''
  @brief return point from index

  @param i     Pixel index
  @param width Image width

  @return Point (x, y)
'''
def i2p(i, width):
    x = i % width
    y = i / width
    return (x, y)


# (function) find neighbor pixels, and update neighbors.
def findNeighbor(focusIdx, ignoreIdx, startDir, offset, width, height, bNeighborType4, tPix, pix):
    global neighbors

    neighbors = []
    for i in range(len(offset)):
        ti = (i + startDir) % 8
        if (bNeighborType4 is True and ti % 2 != 0): continue

        x = offset[ti][0] + (focusIdx % width)
        y = offset[ti][1] + (focusIdx / width)
        testIdx = y * width + x

        # tests:
        if (testIdx != ignoreIdx and # is not ignore?
            (x >= 0 and x < width and y >= 0 and y < height) and # is not outside?
            tPix[testIdx] == 0 and # is not already searched pixel?
            pix[testIdx] > 0): # is white pixel
            neighbors.append((focusIdx, testIdx, offset[ti][2]))

# (function) get direction
def getDirection(focusIdx, targetIdx, offset, width):
    for e in offset:
        x = e[0] + (focusIdx % width)
        y = e[1] + (focusIdx / width)
        testIdx = y * width + x
        if (testIdx == targetIdx):
            return e[2]
    raise ValueError("can't found direction.")




'''
  @brief Divide branched chain.

  @param pix            Input image pixels (unsigned char, single channel)
  @param width          Input image width
  @param height         Input image height
  @param dstPts         Output points array (vector<Point2dArray>)
  @param bNeighborType4 Input image type, true=4-neighbor, false=8-neighbor.

  @return true=Process was succeed
'''
def divideBranchedChain(pix,  width, height, bNeighborType4):
    global neighbors

    dstBuf = [] # std::vector<std::vector<std::array<int, 2> > >

    # offset: [x, y, direction], direction=0...7, 0=right, 1=upper right, ...7=lower right.
    offset = [(1,0,0), (1,-1,1), (0,-1,2), (-1,-1,3), (-1,0,4), (-1,1,5), (0,1,6), (1,1,7)] # std::vector<std::array<int, 3> >

    # segment: [current focused pixel index, neighbor pixel index, neighbor pixel direction]
    neighbors = [] # std::vector<std::array<int, 3> >
    nextSearchPixels = [] # std::vector<std::array<int, 3> >

    tPix = [0] * (width * height) # searched pix

    # scan
    for i in range(width * height):
        if (pix[i] > 0 and tPix[i] == 0):
            firstIdx = i
            focusIdx = firstIdx
            lastFocus = -1
            beginDir = 0
            bFirst = True
            count = 0

            try:
                # find begin point(s) on a segment
                while (count < width * height):
                    findNeighbor(focusIdx, lastFocus, beginDir, offset, width, height, bNeighborType4, tPix, pix)

                    # tests
                    if not neighbors: # empty
                        if bFirst:
                            # single pixel
                            dstBuf.append([i2p(focusIdx, width)])
                            tPix[focusIdx] = 1
                            break
                        # end point
                        nextSearchPixels.append((focusIdx, lastFocus, getDirection(focusIdx, lastFocus, offset, width)))
                        break
                    else:
                        if bFirst:
                            if len(neighbors) == 1:
                                # first pixel is end point
                                nextSearchPixels, neighbors = neighbors, nextSearchPixels # swap
                                break
                        else:
                            if len(neighbors) >= 2 or focusIdx == firstIdx:
                                # branched point, or repeated point
                                neighbors.append((focusIdx, lastFocus, getDirection(focusIdx, lastFocus, offset, width)))
                                nextSearchPixels, neighbors = neighbors, nextSearchPixels # swap
                                break

                    # continue
                    lastFocus = focusIdx
                    focusIdx = neighbors[0][1]
                    beginDir = neighbors[0][2]
                    bFirst = False
                    count += 1
                if count == width * height - 1:
                    raise ValueError("endless loop exception")

                # pick up points on the chains.
                while nextSearchPixels: # not empty
                    bFirst = True
                    lastFocus = -1
                    e = nextSearchPixels.pop(0)
                    firstIdx, beginDir = e[0], e[2]
                    focusIdx = firstIdx
                    count = 0
                    chainPts = [] #Point2dArray

                    while True:
                        findNeighbor(focusIdx, lastFocus, beginDir, offset, width, height, bNeighborType4, tPix, pix)

                        # tests
                        if not neighbors or (bFirst == False and focusIdx == firstIdx):
                            break
                        elif bFirst == False and len(neighbors) >= 2:
                            nextSearchPixels.extend(neighbors)
                            break

                        # continue
                        if bFirst:
                            chainPts.append(i2p(focusIdx, width))
                            tPix[focusIdx] = 1

                        lastFocus = focusIdx
                        focusIdx = neighbors[0][1]
                        beginDir = neighbors[0][2]
                        bFirst = False

                        chainPts.append(i2p(focusIdx, width))
                        tPix[focusIdx] = 1

                        if count >= width * height: break

                    if count == width * height - 1:
                        raise ValueError("endless loop exception")

                    if chainPts: dstBuf.append(chainPts)
            except ValueError as e:
                print e
                return None

    return dstBuf

