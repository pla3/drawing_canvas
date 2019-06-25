#!/usr/bin/env python
#! -*- coding: utf-8 -*-

# base on Panda3D tutorial source;
# Author: Kwasi Mensah
# Date: 7/11/2005

from panda3d.core import loadPrcFileData
#loadPrcFileData("", "window-type offscreen" ) # Spawn an offscreen buffer
#loadPrcFileData("", "audio-library-name null" ) # Prevent ALSA errors
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from panda3d.core import PNMImage, PNMImageHeader
from panda3d.core import PandaNode, LightNode, TextNode
from panda3d.core import Filename
from panda3d.core import NodePath
from panda3d.core import Shader
from panda3d.core import LVecBase4, Point2, Point3
from panda3d.core import Camera
from panda3d.core import deg2Rad
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
import wx

class SceneGenerator():

    def __init__(self):
        self.base = ShowBase()

        #wp = WindowProperties()
        #wp.setSize(640, 480)
        #self.base.win.requestProperties(wp)

        self.base.camera.setPos(0, 0, 0)
        self.base.camLens.setNearFar(0.01, 1000.0)
        self.base.camLens.setFov(50)

        self.base.setBackgroundColor(1, 1, 1)

        if not self.base.win.getGsg().getSupportsBasicShaders():
            print("Toon Shader: Video driver reports that Cg shaders are not supported.")
            return

        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setShader(self.base.loader.loadShader("shader/lightingGen.sha"))
        self.base.cam.node().setInitialState(tempnode.getState())

        light = self.base.render.attachNewNode("light")
        light.setPos(30, -50, 0)

        self.base.render.setShaderInput("light", light)

        normalsBuffer = self.base.win.makeTextureBuffer("normalsBuffer", 0, 0)
        normalsBuffer.setClearColor(LVecBase4(0.5, 0.5, 0.5, 1))
        self.normalsBuffer = normalsBuffer
        normalsCamera = self.base.makeCamera(
            normalsBuffer, lens=self.base.cam.node().getLens())
        normalsCamera.node().setScene(self.base.render)
        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setShader(self.base.loader.loadShader("shader/normalGen.sha"))
        normalsCamera.node().setInitialState(tempnode.getState())

        drawnScene = normalsBuffer.getTextureCard()
        drawnScene.setTransparency(1)
        drawnScene.setColor(1, 1, 1, 0)
        drawnScene.reparentTo(self.base.render2d)
        #self.base.drawnScene = drawnScene

        self.separation = 0.00065
        self.cutoff = 0.3
        inkGen = self.base.loader.loadShader("shader/inkGen.sha")
        drawnScene.setShader(inkGen)
        drawnScene.setShaderInput("separation", LVecBase4(self.separation, 0, self.separation, 0))
        drawnScene.setShaderInput("cutoff", LVecBase4(self.cutoff))

        # Load a model
        #self.smiley = self.loader.loadModel('smiley')
        #self.smiley.reparentTo(self.render)
        #self.smiley.setPos(0, 10.0, 0)

        self.actors = [Actor(), Actor(), Actor(), Actor()]

        self.actors[0].loadModel('models/dekiruo/dekiruo')
        self.actors[0].reparentTo(self.base.render)
        self.actors[0].loadAnims({'normal': 'models/dekiruo/dekiruo-Anim_normal'})
        self.actors[0].loadAnims({'anger': 'models/dekiruo/dekiruo-Anim_anger'})
        self.actors[0].loadAnims({'sadness2crying': 'models/dekiruo/dekiruo-Anim_sadness2crying'})
        self.actors[0].loadAnims({'sleep': 'models/dekiruo/dekiruo-Anim_sleep'})
        self.actors[0].loadAnims({'smile': 'models/dekiruo/dekiruo-Anim_smile'})
        self.actors[0].loadAnims({'surprised': 'models/dekiruo/dekiruo-Anim_surprised'})

        for i in range(1, len(self.actors)):
            self.actors[i].loadModel('models/dekinaio/dekinaio')
            self.actors[i].reparentTo(self.base.render)
            self.actors[i].loadAnims({'normal': 'models/dekinaio/dekinaio-Anim_normal'})
            self.actors[i].loadAnims({'anger': 'models/dekinaio/dekinaio-Anim_anger'})
            self.actors[i].loadAnims({'sadness2crying': 'models/dekinaio/dekinaio-Anim_sadness2crying'})
            self.actors[i].loadAnims({'sleep': 'models/dekinaio/dekinaio-Anim_sleep'})
            self.actors[i].loadAnims({'smile': 'models/dekinaio/dekinaio-Anim_smile'})
            self.actors[i].loadAnims({'surprised': 'models/dekinaio/dekinaio-Anim_surprised'})

        self.info = None  # frame集合体(page)のxml
        self.actors_dict = {} # 名前付けされた役者

    # xmlから場面を作る。(現時点では登場人物の列挙)
    def buildScene(self, reverse=False):
        characters = self.info.findall('.//character')
        if reverse is True: characters.reverse()

        if len(characters) > len(self.actors):
            print('character numbers over')
            return

        if len(characters) == 1:
            self.actors[0].setPos((0, -100.0, 0))
            self.actors_dict[characters[0].find('name').text] = self.actors[0]
        elif len(characters) == 2:
            self.actors[0].setPos((-10.0, -100.0, 0))
            self.actors[1].setPos((10.0, -100.0, 0))
            self.actors_dict[characters[0].find('name').text] = self.actors[0]
            self.actors_dict[characters[1].find('name').text] = self.actors[1]
        elif len(characters) == 3:
            self.actors[0].setPos((0.0, -100.0, 0))
            self.actors[1].setPos((-15.0, -100.0, 0))
            self.actors[2].setPos((15.0, -100.0, 0))
            self.actors_dict[characters[0].find('name').text] = self.actors[0]
            self.actors_dict[characters[1].find('name').text] = self.actors[1]
            self.actors_dict[characters[2].find('name').text] = self.actors[2]
        elif len(characters) == 4:
            self.actors[0].setPos((10.0, -100.0, 0))
            self.actors[1].setPos((-10.0, -100.0, 0))
            self.actors[2].setPos((20.0, -100.0, 0))
            self.actors[3].setPos((-20.0, -100.0, 0))
            self.actors_dict[characters[0].find('name').text] = self.actors[0]
            self.actors_dict[characters[1].find('name').text] = self.actors[1]
            self.actors_dict[characters[2].find('name').text] = self.actors[2]
            self.actors_dict[characters[3].find('name').text] = self.actors[3]

    def makeFrames(self):
        for i, frame in enumerate(self.info.findall('.//frame')):

            # コマ内の登場人物の表情の変更
            for chara in frame.findall('character'):
                actor = self.actors_dict[chara.find('name').text]
                emo = chara.find('face').attrib['emo']
                # 表情をセット
                actor.play('normal')
                actor.pose(self.actors[i].getCurrentAnim(), 0)
                actor.play(emo)
                actor.pose(self.actors[i].getCurrentAnim(), random.randrange(0, 99))

            print('frame_'+f'zero padding: {i:02}'+'.png')
            self.saveImage('frame_'+f'zero padding: {i:02}'+'.png')

    def make(self, xml_path, reverse=False):
        self.loadXml(xml_path)

        for actor in self.actors:
            actor.setPos((0, -100.0, 0))

        characters = self.info.findall('character')
        if reverse is True: characters.reverse()

        for i, chara in enumerate(characters):
            if i >= len(self.actors):
                name = os.path.splitext(xml_path)[0].split('/')[-1]
                print(name)
                break
            actor = self.actors[i]

            coord = chara.find('face').attrib
            dir = coord.get('dir')
            emo = coord.get('emo')
            x1 = float(coord.get('x1')) * 2.0 - 1.0
            y1 = float(coord.get('y1')) * -2.0 + 1.0
            x2 = float(coord.get('x2')) * 2.0 - 1.0
            y2 = float(coord.get('y2')) * -2.0 + 1.0

            # set position
            p1, p2 = ((x1+x2)/2.0, y2),  ((x1+x2)/2.0, y1)
            self._fit(actor, p1, p2)

            # set direction front = 0.0, left = -45.0, right = 45.0, rear = 180.0
            h = random.uniform(-10.0, 10.0)
            if dir == 'left':
                h = random.uniform(-45.0, -100.0)
            elif dir == 'right':
                h = random.uniform(45.0, 100.0)
            elif dir == 'front':
                h = random.uniform(-10.0, 10.0)
            elif dir == 'rear':
                h = random.uniform(170.0, 190.0)
            actor.setHpr(h, 0.0, 0.0)

            # set emotion
            actor.play('normal')
            actor.pose(self.actors[i].getCurrentAnim(), 0)
            actor.play(emo)
            actor.pose(self.actors[i].getCurrentAnim(), random.randrange(0, 99))

            # debug
            #print dir, emo
            #OnscreenText(text='+', fg=(0, 0, 1, 1), pos=(x1, y1), scale=.05)
            #OnscreenText(text='+', fg=(0, 0, 1, 1), pos=(x1, y2), scale=.05)
            #OnscreenText(text='+', fg=(0, 0, 1, 1), pos=(x2, y2), scale=.05)
            #OnscreenText(text='+', fg=(0, 0, 1, 1), pos=(x2, y1), scale=.05)
            #OnscreenText(text='P1', fg=(0, 0, 1, 1), pos=(p1[0], p1[1]), scale=.05)
            #OnscreenText(text='P2', fg=(0, 0, 1, 1), pos=(p2[0], p2[1]), scale=.05)
            #OnscreenText(text='camera: ' + str(self.camera.getPos()), fg=(1, 0, 0, 1), pos=(-0.5, -0.95), scale=.05)

        self.saveImage()

    def loadXml(self, xmlpath):
        self.info = ComicInfo.read_page(xmlpath)

    def saveImage(self, path='testImg.png'):
        self.base.graphicsEngine.renderFrame() # Rendering the frame
        self.base.graphicsEngine.renderFrame() # Rendering the frame
        image = PNMImage()
        dr = self.base.camNode.getDisplayRegion(0)
        dr.getScreenshot(image)
        image.removeAlpha()
        image.write(Filename(path))

        # pre process for skeltonization
        gray = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
        gray[gray < 150] = 0
        gray[gray >= 150] = 255
        kernel = np.ones((3, 3), np.uint8)
        gray = cv2.erode(gray, kernel)
        #gray = cv2.dilate(gray, kernel)
        #gray = cv2.resize(gray, (gray.shape[1]/2, gray.shape[0]/2))
        
        cv2.imwrite(path, gray)
        '''
        '''

    def _fit(self, c, p1, p2):
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
            hfov = self.base.camLens.getHfov()
            w = math.fabs(self.base.a2dRight)
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
            vfov = self.base.camLens.getVfov()
            h = math.fabs(self.base.a2dTop)
            theta = (vfov / 2.0) * (p1[1] / h)
            Q = math.fabs(p2[1] - p1[1])
            O = dist3d
            n = p1[1] * O / Q
            d = n / math.tan(deg2Rad(theta))
            p_1 = Point3(p1[0], d, p1[1])
            p_2 = Point3(p2[0], d, p2[1])
            p = Point3(p1[0], d, n + offset[1])


        c.setPos(p)

class BalloonGenerator():

    def __init__(self, wxPanel):
        self.panel = wxPanel

    def make(self, xmlpath):
        self.loadXml(xmlpath)

        width, height = self.panel.GetClientSize().width, self.panel.GetClientSize().height
        bdc = wx.BufferedDC(wx.ClientDC(self.panel), self.panel.buffer)

        balloons = self.info.findall('balloon')
        b_size = len(balloons)
        balloon_layout = [1.0]
        for i in reversed(range(b_size - 1)):
            step = 1.0 / float(b_size - 1)
            balloon_layout.append(step * i)

        for i, balloon in enumerate(balloons):
            # draw shape
            coord = balloon.find('coord').attrib
            x1, y1, x2, y2 = float(coord['x1']), float(coord['y1']), float(coord['x2']), float(coord['y2'])
            w, h = width * (x2 - x1), height * (y2 - y1)
            x_offset = w * 0.2 * (balloon_layout[i] - 0.5)
            x, y = width * balloon_layout[i] - w * 0.5 - x_offset, 0.0 - h * 0.3
            bdc.SetPen(wx.Pen('black', height * 0.01))
            bdc.SetBrush(wx.Brush('white'))
            bdc.DrawEllipse(x, y, w, h)
            '''
            # draw text
            #TODO: 縦書き
            rw, rh = min((x + w), width) - x, h + y
            #bdc.SetPen(wx.Pen('red', 3.0)) # for debug
            #bdc.DrawCircle(x + rw / 2, 0.0 + rh / 2, 1) # for debug
            dialog_texts = balloon.find('dialog').text.split(' ')
            for j, text in enumerate(dialog_texts):
                bdc.SetTextForeground((0,0,0))
                bdc.DrawText(text, x + rw * 0.1, rh * 0.25 + 20 * j)
            '''

    def loadXml(self, xmlpath):
        self.info = ComicInfo.read(xmlpath)

class FrameGenerator():

    def __init__(self, wxPanel):
        #self.dc = wxPanel
        #w, h = wxPanel
        pass

    def make(self, xmlpath):
        pass

#s = SceneGenerator()
#s.make()
#b = BalloonGenerator()
#b.make()
