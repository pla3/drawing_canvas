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

        '''
        cam1 = Camera('cam1')
        cam1.getLens().setNear(0.01)
        cam1.getLens().setFov(50)
        cam1.showFrustum()
        camera1 = self.render.attachNewNode(cam1)
        camera1.setName('camera1')
        camera1.setPos(0, -6, 3)

        cam2 = Camera('cam2')
        cam2.getLens().setNear(0.01)
        cam2.getLens().setFov(50)
        #cam2.showFrustum()
        camera2 = self.render.attachNewNode(cam2)
        camera2.setName('camera2')
        camera2.setPos(0, -6, 3)
        '''

        self.disableMouse()
        #self.cam = camera2
        #self.lens = self.cam.node().getLens()
        self.camera.setPos(0, -6, 3.2)
        self.camLens.setNearFar(0.01, 1000.0)
        self.camLens.setFov(50)
        #self.cam.node().setLodScale(math.tan(math.radians(100.0 * 0.5)))

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

        # Load a model and start its animation.
        self.character = Actor()
        #self.character.loadModel('models/miku/tda_miku')
        #self.character.loadAnims({'anim': 'models/miku/tda_miku-Anim0'})
        #self.character.listJoints()
        #node = self.character.find('**/*modelRoot')
        #geom_node = node.getChildren()[0].node()
        #geoms = geom_node.getGeoms()
        #for child in node.getChildren():
        #    print child

        self.character.loadModel('models/dekiruo/dekiruo')
        self.character.reparentTo(self.render)
        self.character.ls()

        self.character.loadAnims({'normal': 'models/dekiruo/dekiruo-Anim_normal'})
        self.character.play('normal')
        #self.character.loadAnims({'anger': 'models/dekiruo/dekiruo-Anim_anger'})
        #self.character.play('anger')
        #self.character.loadAnims({'sadness2crying': 'models/dekiruo/dekiruo-Anim_sadness2crying'})
        #self.character.play('sadness2crying')
        #self.character.loadAnims({'sleep': 'models/dekiruo/dekiruo-Anim_sleep'})
        #self.character.play('sleep')
        #self.character.loadAnims({'smile': 'models/dekiruo/dekiruo-Anim_smile'})
        #self.character.play('smile')
        #self.character.loadAnims({'surprised': 'models/dekiruo/dekiruo-Anim_surprised'})
        #self.character.play('surprised')

        #self.character.loadModel('models/dekinaio/dekinaio')
        #self.character.reparentTo(self.render)
        #self.character.ls()

        #self.character.loadAnims({'normal': 'models/dekinaio/dekinaio-Anim_normal'})
        #self.character.play('normal')
        #self.character.loadAnims({'anger': 'models/dekinaio/dekinaio-Anim_anger'})
        #self.character.play('anger')
        #self.character.loadAnims({'sadness2crying': 'models/dekinaio/dekinaio-Anim_sadness2crying'})
        #self.character.play('sadness2crying')
        #self.character.loadAnims({'sleep': 'models/dekinaio/dekinaio-Anim_sleep'})
        #self.character.play('sleep')
        #self.character.loadAnims({'smile': 'models/dekinaio/dekinaio-Anim_smile'})
        #self.character.play('smile')
        #self.character.loadAnims({'surprised': 'models/dekinaio/dekinaio-Anim_surprised'})
        #self.character.play('surprised')

        #anim =  self.character.getCurrentAnim()
        #frames = self.character.getNumFrames(anim)
        #print anim, frames
        #self.character.pose(anim, int(frames * 0.9))

        # Create smiley's node to indicate 3d points
        self.smileyActor1 = self.render.attachNewNode('SmileyActorNode1')
        self.smileyActor2 = self.render.attachNewNode('SmileyActorNode2')
        smiley = self.loader.loadModel('smiley')
        smiley.setScale(0.01, 0.01, 0.01)
        smiley.instanceTo(self.smileyActor1)
        smiley.instanceTo(self.smileyActor2)

        n1 = self.character.exposeJoint(None, "modelRoot", "Eyes")
        n2 = self.character.exposeJoint(None, "modelRoot", "Head")

        self.label1 = OnscreenText(text='P1', fg=(1, 0, 0, 1), pos=(0, 0), scale=.05, mayChange=1)
        self.label2 = OnscreenText(text='P2', fg=(1, 0, 0, 1), pos=(0, 0), scale=.05, mayChange=1)
        self.info1 = OnscreenText(text='dist3d:', fg=(1, 0, 0, 1), pos=(-1, 0), scale=.05, mayChange=1)
        self.info2 = OnscreenText(text='dist2d:', fg=(1, 0, 0, 1), pos=(-1, -0.1), scale=.05, mayChange=1)
        self.info3 = OnscreenText(text='camera:', fg=(1, 0, 0, 1), pos=(-1, -0.2), scale=.05, mayChange=1)

        self.taskMgr.add(self.lookAt, 'lookAt', extraArgs=[n1, n2])
        self.taskMgr.add(self.updateNamePos, 'name pos update', extraArgs=[n1, n2])

        # These allow you to change cartooning parameters in realtime
        self.accept("escape", sys.exit, [0])
        self.accept("arrow_up", self.camera_f) #self.increaseSeparation)
        self.accept("arrow_down", self.camera_b) #self.decreaseSeparation)
        self.accept("arrow_left", self.camera_l) #self.increaseCutoff)
        self.accept("arrow_right", self.camera_r) #self.decreaseCutoff)
        self.accept("s", self.saveImage)
        self.accept("p", self.play)
        self.accept("o", self.stop)
        self.accept("n", self.forward)
        self.accept("b", self.rewind)
        self.accept("l", self.lookAt)
        self.accept("h", self.hide)
        self.accept("1", self.cam_closeup)
        self.accept("2", self.cam_bustshot)
        self.accept("3", self.cam_longshot)

    def decide_camera_distance(self, face_length):
        pass #顔の大きさが決まったら対象からカメラの距離を返す。TODO

    def cam_closeup(self):
        self.camera.setPos(self.render, (0, -1.0, 3.2))

    def cam_bustshot(self):
        self.camera.setPos(self.render, (0, -2.0, 3.2))

    def cam_longshot(self):
        self.camera.setPos(self.render, (0, -10.0, 3.2))

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

    def saveImage(self):
        self.graphicsEngine.renderFrame()
        image = PNMImage()
        dr = self.camNode.getDisplayRegion(0)
        dr.getScreenshot(image)
        image.write(Filename('testImg.png'))

    def play(self):
        frame = self.character.getCurrentFrame('anim')
        self.character.play('anim', fromFrame=frame)

    def stop(self):
        frame = self.character.getCurrentFrame('anim')
        self.character.pose('anim', frame)

    def forward(self):
        frame = self.character.getCurrentFrame('anim') + 10
        frame = min(frame, self.character.getNumFrames('anim'))
        self.character.pose('anim', frame)

    def rewind(self):
        frame = self.character.getCurrentFrame('anim') - 10
        frame = max(0, frame)
        self.character.pose('anim', frame)

    def lookAt(self, node1, node2):
        pos1 = node1.getPos(self.render)
        pos2 = node2.getPos(self.render)
        self.camera.lookAt((pos1 + pos2) / 2.0, (0, 0, 1))
        return Task.cont

    def hide(self):
        if self.character.isHidden():
            self.character.show()
        else:
            self.character.hide()

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


    def updateNamePos(self, node1, node2):
        # show 3d points
        self.smileyActor1.setPos(node1.getPos(self.render))
        self.smileyActor2.setPos(node2.getPos(self.render))

        # show 2d points
        pos1 = self.map3dToAspect2d(self.render, node1.getPos(self.render))
        if pos1 == None:
            self.label1.hide()
        else:
            self.label1['pos'] = (pos1[0], pos1[2])
            self.label1.show()
        pos2 = self.map3dToAspect2d(self.render, node2.getPos(self.render))
        if pos2 == None:
            self.label2.hide()
        else:
            self.label2['pos'] = (pos2[0], pos2[2])
            self.label2.show()

        dist3dc = (node2.getPos(self.render)-node1.getPos(self.render)).length()
        dist3d = node2.getPos(node1).length()
        self.info1['text'] = 'dist3d: '+ str(dist3d)

        if pos1 != None and pos2 != None:
            dist2d = (pos2-pos1).length()
            dist_cam = 4.0 * (dist3d / dist2d)
        else:
            dist2d = None
            dist_cam = None
        self.info2['text'] = 'dist2d: '+ str(dist2d)

        cam_pos = self.camera.getPos()
        self.info3['text'] = 'camera: ' + str(cam_pos) + ' dist_cam: ' + str(dist_cam)
        # -10.0 <-> -1.0

        return Task.cont

t = ToonMaker()
t.run()
