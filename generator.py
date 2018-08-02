#!/usr/bin/env python
#! -*- coding: utf-8 -*-

# Author: Kwasi Mensah
# Date: 7/11/2005
#
# This is a tutorial to show some of the more advanced things
# you can do with Cg. Specifically, with Non Photo Realistic
# effects like Toon Shading. It also shows how to implement
# multiple buffers in Panda.

from direct.showbase.ShowBase import ShowBase
from panda3d.core import PNMImage, PNMImageHeader
from panda3d.core import PandaNode, LightNode, TextNode
from panda3d.core import Filename
from panda3d.core import NodePath
from panda3d.core import Shader
from panda3d.core import LVecBase4, Point2, Point3
from panda3d.core import Camera
from panda3d.core import deg2Rad
from direct.task.Task import Task
from direct.actor.Actor import Actor
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.showbase.BufferViewer import BufferViewer
from pandac.PandaModules import LineSegs
import sys
import os
import math
import random
from lib_comic_info import Panel, ComicInfo
import cv2
import numpy as np


class ToonMaker(ShowBase):

    def __init__(self):
        # Initialize the ShowBase class from which we inherit, which will
        # create a window and set up everything we need for rendering into it.
        ShowBase.__init__(self)

        self.disableMouse()
        self.camera.setPos(0, 0, 0)
        self.camLens.setNearFar(0.01, 1000.0)
        self.camLens.setFov(50)

        self.setBackgroundColor(1, 1, 1)

        if not self.win.getGsg().getSupportsBasicShaders():
            print("Toon Shader: Video driver reports that Cg shaders are not supported.")
            return

        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setShader(self.loader.loadShader("shader/lightingGen.sha"))
        self.cam.node().setInitialState(tempnode.getState())

        light = self.render.attachNewNode("light")
        light.setPos(30, -50, 0)

        self.render.setShaderInput("light", light)

        normalsBuffer = self.win.makeTextureBuffer("normalsBuffer", 0, 0)
        normalsBuffer.setClearColor(LVecBase4(0.5, 0.5, 0.5, 1))
        self.normalsBuffer = normalsBuffer
        normalsCamera = self.makeCamera(
            normalsBuffer, lens=self.cam.node().getLens())
        normalsCamera.node().setScene(self.render)
        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setShader(self.loader.loadShader("shader/normalGen.sha"))
        normalsCamera.node().setInitialState(tempnode.getState())

        drawnScene = normalsBuffer.getTextureCard()
        drawnScene.setTransparency(1)
        drawnScene.setColor(1, 1, 1, 0)
        drawnScene.reparentTo(self.render2d)
        self.drawnScene = drawnScene

        self.separation = 0.00065
        self.cutoff = 0.3
        inkGen = self.loader.loadShader("shader/inkGen.sha")
        drawnScene.setShader(inkGen)
        drawnScene.setShaderInput("separation", LVecBase4(self.separation, 0, self.separation, 0))
        drawnScene.setShaderInput("cutoff", LVecBase4(self.cutoff))

        # Load a model
        #self.smiley = self.loader.loadModel('smiley')
        #self.smiley.reparentTo(self.render)
        #self.smiley.setPos(0, 10.0, 0)

        self.character = [Actor(), Actor(), Actor()]

        self.character[0].loadModel('models/dekiruo/dekiruo')
        self.character[0].reparentTo(self.render)
        self.character[0].loadAnims({'normal': 'models/dekiruo/dekiruo-Anim_normal'})
        self.character[0].loadAnims({'anger': 'models/dekiruo/dekiruo-Anim_anger'})
        self.character[0].loadAnims({'sadness2crying': 'models/dekiruo/dekiruo-Anim_sadness2crying'})
        self.character[0].loadAnims({'sleep': 'models/dekiruo/dekiruo-Anim_sleep'})
        self.character[0].loadAnims({'smile': 'models/dekiruo/dekiruo-Anim_smile'})
        self.character[0].loadAnims({'surprised': 'models/dekiruo/dekiruo-Anim_surprised'})

        self.character[1].loadModel('models/dekinaio/dekinaio')
        self.character[1].reparentTo(self.render)
        self.character[1].loadAnims({'normal': 'models/dekinaio/dekinaio-Anim_normal'})
        self.character[1].loadAnims({'anger': 'models/dekinaio/dekinaio-Anim_anger'})
        self.character[1].loadAnims({'sadness2crying': 'models/dekinaio/dekinaio-Anim_sadness2crying'})
        self.character[1].loadAnims({'sleep': 'models/dekinaio/dekinaio-Anim_sleep'})
        self.character[1].loadAnims({'smile': 'models/dekinaio/dekinaio-Anim_smile'})
        self.character[1].loadAnims({'surprised': 'models/dekinaio/dekinaio-Anim_surprised'})

        self.accept("escape", sys.exit, [0])
        self.accept("arrow_up", self.camera_f)
        self.accept("arrow_down", self.camera_b)
        self.accept("arrow_left", self.camera_l)
        self.accept("arrow_right", self.camera_r)
        self.accept("m", self.make)
        self.accept("c", self.check)

    def make(self):
        # load xml
        info = ComicInfo.read('xmls/OL_Lunch_033_r_03.xml')
        for i, chara in enumerate(info.findall('character')):
            coord = chara.find('face').attrib
            dir = coord.get('dir')
            emo = coord.get('emo')
            x1 = float(coord.get('x1')) * 2.0 - 1.0
            y1 = float(coord.get('y1')) * -2.0 + 1.0
            x2 = float(coord.get('x2')) * 2.0 - 1.0
            y2 = float(coord.get('y2')) * -2.0 + 1.0

            # set position
            p1, p2 = ((x1+x2)/2.0, y2),  ((x1+x2)/2.0, y1)
            self.fit(self.character[i], p1, p2)

            # set direction front = 0.0, left = -45.0, right = 45.0, rear = 180.0
            if dir == 'left':
                h = random.uniform(-45.0, -100.0)
            elif dir == 'right':
                h = random.uniform(45.0, 100.0)
            elif dir == 'front':
                h = random.uniform(-10.0, 10.0)
            elif dir == 'rear':
                h = random.uniform(170.0, 190.0)
            self.character[i].setHpr(h, 0.0, 0.0)

            # set emotion
            #emo = 'normal'
            self.character[i].play(emo)
            self.character[i].pose(self.character[i].getCurrentAnim(), random.randrange(0, 99))

            # debug
            print dir, emo
            #OnscreenText(text='+', fg=(0, 0, 1, 1), pos=(x1, y1), scale=.05)
            #OnscreenText(text='+', fg=(0, 0, 1, 1), pos=(x1, y2), scale=.05)
            #OnscreenText(text='+', fg=(0, 0, 1, 1), pos=(x2, y2), scale=.05)
            #OnscreenText(text='+', fg=(0, 0, 1, 1), pos=(x2, y1), scale=.05)
            #OnscreenText(text='P1', fg=(0, 0, 1, 1), pos=(p1[0], p1[1]), scale=.05)
            #OnscreenText(text='P2', fg=(0, 0, 1, 1), pos=(p2[0], p2[1]), scale=.05)
            #OnscreenText(text='camera: ' + str(self.camera.getPos()), fg=(1, 0, 0, 1), pos=(-0.5, -0.95), scale=.05)

            self.saveImage()

    def saveImage(self):
        self.graphicsEngine.renderFrame()
        image = PNMImage()
        dr = self.camNode.getDisplayRegion(0)
        dr.getScreenshot(image)
        image.write(Filename('testImg.png'))

        # process for skeltonization
        img = cv2.imread('testImg.png', -1)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray[gray < 127] = 0
        gray[gray >= 127] = 255

        kernel = np.ones((6, 6), np.uint8)
        gray = cv2.erode(gray, kernel)
        gray = cv2.dilate(gray, kernel)

        cv2.imwrite("testImg.png", gray)


    def check(self):
        # check model info
        i = 0
        self.character[i].ls()
        self.character[i].listJoints()
        node = self.character[i].find('**/*modelRoot')
        geom_node = node.getChildren()[0].node()
        geoms = geom_node.getGeoms()
        for child in node.getChildren():
            print child

    def camera_f(self):
        pos = self.camera.getPos(self.render)
        self.camera.setPos(pos[0], pos[1]+0.1, pos[2])

    def camera_b(self):
        pos = self.camera.getPos(self.render)
        self.camera.setPos(pos[0], pos[1]-0.1, pos[2])

    def camera_r(self):
        pos = self.camera.getPos(self.render)
        self.camera.setPos(pos[0]+0.1, pos[1], pos[2])

    def camera_l(self):
        pos = self.camera.getPos(self.render)
        self.camera.setPos(pos[0]-0.1, pos[1], pos[2])

    def fit(self, c, p1, p2):
        #bound = c.getBounds()
        #r = bound.getRadius()
        #cp = c.getPos(self.render)
        #offset = Point3(0.0, r, 0.0)
        #dist3d  = r * 2.0
        n1 = c.exposeJoint(None, "modelRoot", "Head")
        n2 = c.exposeJoint(None, "modelRoot", "Eyes")
        n_root = c.exposeJoint(None, "modelRoot", "ParentNode")
        offset = n_root.getPos(n1)
        dist3d = n2.getPos(n1).length()

        if p1[0] != 0.0:
            hfov = self.camLens.getHfov()
            w = math.fabs(self.a2dRight)
            a = p1[0]
            Q = math.fabs(p2[1] - p1[1])
            O = dist3d
            n = p1[1] * O / Q
            A = a * O / Q
            theta = (hfov / 2.0) * (a / w)
            d = A / math.tan(deg2Rad(theta))
            p_1 = Point3(A, d, n)
            p_2 = Point3(A, d, n + O)
            p = Point3(A, d, n + offset[1])
        else:
            vfov = self.camLens.getVfov()
            h = math.fabs(self.a2dTop)
            theta = (vfov / 2.0) * (p1[1] / h)
            Q = math.fabs(p2[1] - p1[1])
            O = dist3d
            n = p1[1] * O / Q
            d = n / math.tan(deg2Rad(theta))
            p_1 = Point3(p1[0], d, p1[1])
            p_2 = Point3(p2[0], d, p2[1])
            p = Point3(p1[0], d, n + offset[1])


        c.setPos(p)

t = ToonMaker()
t.run()
