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
import sys
import os
import math


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

        # Check video card capabilities.
        if not self.win.getGsg().getSupportsBasicShaders():
            print("Toon Shader: Video driver reports that Cg shaders are not supported.")
            return

        # This shader's job is to render the model with discrete lighting
        # levels.  The lighting calculations built into the shader assume
        # a single nonattenuating point light.
        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setShader(self.loader.loadShader("shader/lightingGen.sha"))
        self.cam.node().setInitialState(tempnode.getState())

        # This is the object that represents the single "light", as far
        # the shader is concerned.  It's not a real Panda3D LightNode, but
        # the shader doesn't care about that.
        light = self.render.attachNewNode("light")
        light.setPos(30, -50, 0)

        # this call puts the light's nodepath into the render state.
        # this enables the shader to access this light by name.
        self.render.setShaderInput("light", light)

        # The "normals buffer" will contain a picture of the model colorized
        # so that the color of the model is a representation of the model's
        # normal at that point.
        normalsBuffer = self.win.makeTextureBuffer("normalsBuffer", 0, 0)
        normalsBuffer.setClearColor(LVecBase4(0.5, 0.5, 0.5, 1))
        self.normalsBuffer = normalsBuffer
        normalsCamera = self.makeCamera(
            normalsBuffer, lens=self.cam.node().getLens())
        normalsCamera.node().setScene(self.render)
        tempnode = NodePath(PandaNode("temp node"))
        tempnode.setShader(self.loader.loadShader("shader/normalGen.sha"))
        normalsCamera.node().setInitialState(tempnode.getState())
        # what we actually do to put edges on screen is apply them as a texture to
        # a transparent screen-fitted card
        drawnScene = normalsBuffer.getTextureCard()
        drawnScene.setTransparency(1)
        drawnScene.setColor(1, 1, 1, 0)
        drawnScene.reparentTo(self.render2d)
        self.drawnScene = drawnScene

        # this shader accepts, as input, the picture from the normals buffer.
        # it compares each adjacent pixel, looking for discontinuities.
        # wherever a discontinuity exists, it emits black ink.
        self.separation = 0.00065
        self.cutoff = 0.3
        inkGen = self.loader.loadShader("shader/inkGen.sha")
        drawnScene.setShader(inkGen)
        drawnScene.setShaderInput("separation", LVecBase4(self.separation, 0, self.separation, 0))
        drawnScene.setShaderInput("cutoff", LVecBase4(self.cutoff))

        self.label1 = OnscreenText(text='P_1', fg=(1, 0, 0, 1), pos=(0, 0), scale=.05, mayChange=1)
        self.label2 = OnscreenText(text='P_2', fg=(1, 0, 0, 1), pos=(0, 0), scale=.05, mayChange=1)
        self.label3 = OnscreenText(text='P1', fg=(0, 0, 1, 1), pos=(0, 0), scale=.05, mayChange=1)
        self.label4 = OnscreenText(text='P2', fg=(0, 0, 1, 1), pos=(0, 0), scale=.05, mayChange=1)
        self.info3 = OnscreenText(text='camera:', fg=(1, 0, 0, 1), pos=(-1, -0.2), scale=.05, mayChange=1)

        # Load a model
        #self.smiley = self.loader.loadModel('smiley')
        #self.smiley.reparentTo(self.render)
        #self.smiley.setPos(0, 10.0, 0)

        self.character = [Actor(), Actor()]

        self.character[0].loadModel('models/dekiruo/dekiruo')
        self.character[0].reparentTo(self.render)
        self.character[0].loadAnims({'anim': 'models/dekiruo/dekiruo-Anim_anger'})
        self.character[0].play('anim')
        self.character[0].pose('anim', 0)

        self.character[1].loadModel('models/dekiruo/dekinaio')
        self.character[1].reparentTo(self.render)

        #print self.character.getNumFrames('anim')
        #self.character.setHpr(0.0, 0.0, 0.0) # front
        #self.character.setHpr(-45.0, 0.0, 0.0) # left
        #self.character[0].setHpr(45.0, 0.0, 0.0) # right
        self.character[0].setHpr(-45.0, 0.0, 0.0) # left
        self.character[1].setHpr(45.0, 0.0, 0.0) # right

        # check model info
        #self.character.ls()
        #self.character.listJoints()
        #node = self.character.find('**/*modelRoot')
        #geom_node = node.getChildren()[0].node()
        #geoms = geom_node.getGeoms()
        #for child in node.getChildren():
        #    print child

        c0_p1 = (0.1, -0.1)
        c0_p2 = (0.1, 0.2)
        c1_p1 = (-0.5, -0.1)
        c1_p2 = (-0.5, 0.2)

        self.updateNamePos(self.character[0])
        self.fit(self.character[0], c0_p1, c0_p2)
        self.updateNamePos(self.character[1])
        self.fit(self.character[1], c1_p1, c1_p2)

        #self.taskMgr.add(self.updateNamePos, 'name pos update 0', extraArgs=[self.character[0]])
        #self.taskMgr.add(self.fit, 'fit pos update 0', extraArgs=[self.character[0], c0_p1, c0_p2])
        #self.taskMgr.add(self.updateNamePos, 'name pos update 1', extraArgs=[self.character[1]])
        #self.taskMgr.add(self.fit, 'fit pos update 1', extraArgs=[self.character[1], c1_p1, c1_p2])

        # These allow you to change cartooning parameters in realtime
        self.accept("escape", sys.exit, [0])
        self.accept("arrow_up", self.camera_f) #self.increaseSeparation)
        self.accept("arrow_down", self.camera_b) #self.decreaseSeparation)
        self.accept("arrow_left", self.camera_l) #self.increaseCutoff)
        self.accept("arrow_right", self.camera_r) #self.decreaseCutoff)

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

    def increaseSeparation(self):
        self.separation = self.separation * 1.11111111
        print("separation: %f" % (self.separation))
        self.drawnScene.setShaderInput(
            "separation", LVecBase4(self.separation, 0, self.separation, 0))

    def decreaseSeparation(self):
        self.separation = self.separation * 0.90000000
        print("separation: %f" % (self.separation))
        self.drawnScene.setShaderInput(
            "separation", LVecBase4(self.separation, 0, self.separation, 0))

    def increaseCutoff(self):
        self.cutoff = self.cutoff * 1.11111111
        print("cutoff: %f" % (self.cutoff))
        self.drawnScene.setShaderInput("cutoff", LVecBase4(self.cutoff))

    def decreaseCutoff(self):
        self.cutoff = self.cutoff * 0.90000000
        print("cutoff: %f" % (self.cutoff))
        self.drawnScene.setShaderInput("cutoff", LVecBase4(self.cutoff))

    def map3dToAspect2d(self, node, point):
        """Maps the indicated 3-d point (a Point3), which is relative to
        the indicated NodePath, to the corresponding point in the aspect2d
        scene graph. Returns the corresponding Point3 in aspect2d.
        Returns None if the point is not onscreen. """

        # Convert the point to the 3-d space of the camera
        p3 = self.camera.getRelativePoint(node, point)
        # Convert it through the lens to render2d coordinates
        p2 = Point2()
        if not self.camLens.project(p3, p2):
           return None
        r2d = Point3(p2[0], 0, p2[1])
        # And then convert it to aspect2d coordinates
        a2d = self.aspect2d.getRelativePoint(self.render2d, r2d)
        return a2d


    def updateNamePos(self, c):
        #bound = c.getBounds()
        #r = bound.getRadius()
        #cp = c.getPos(self.render)
        #p1 = cp + Point3(0.0, 0.0, -r)
        #p2 = cp + Point3(0.0, 0.0, r)
        n1 = c.exposeJoint(None, "modelRoot", "Head")
        n2 = c.exposeJoint(None, "modelRoot", "Eyes")
        p1 = n1.getPos(self.render)
        p2 = n2.getPos(self.render)

        # show 2d points
        pos1 = self.map3dToAspect2d(self.render, p1)
        if pos1 == None:
            self.label1.hide()
        else:
            self.label1['pos'] = (pos1[0], pos1[2])
            self.label1.show()
        pos2 = self.map3dToAspect2d(self.render, p2)
        if pos2 == None:
            self.label2.hide()
        else:
            self.label2['pos'] = (pos2[0], pos2[2])
            self.label2.show()

        cam_pos = self.camera.getPos()
        self.info3['text'] = 'camera: ' + str(cam_pos)

        return Task.cont

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

        # show 2d points
        self.label3['pos'] = (p1[0], p1[1])
        self.label3.show()
        self.label4['pos'] = (p2[0], p2[1])
        self.label4.show()

        return Task.cont

t = ToonMaker()
t.run()
