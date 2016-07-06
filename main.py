#!/usr/bin/env python

# Author: Ryan Myers
# Models: Jeff Styers, Reagan Heller
#
# Last Updated: 2015-03-13
#
# This tutorial provides an example of creating a character
# and having it walk around on uneven terrain, as well
# as implementing a fully rotatable camera.

#from direct.showbase.DirectObject import DirectObject
#from direct.gui.DirectGui import *
#from direct.interval.IntervalGlobal import *
from panda3d.core import lookAt
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
from panda3d.core import Texture, GeomNode
from panda3d.core import PerspectiveLens
from panda3d.core import CardMaker
from panda3d.core import Light, Spotlight
from panda3d.core import TextNode
from panda3d.core import LVector3

from direct.showbase.ShowBase import ShowBase
from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionBox, CollisionSphere, CollisionPolygon, Point3
from panda3d.core import CollisionHandlerQueue, CollisionHandlerPusher, CollisionRay
from panda3d.core import Filename, AmbientLight, DirectionalLight
from panda3d.core import PandaNode, NodePath, Camera, TextNode
from panda3d.core import CollideMask
from direct.gui.OnscreenText import OnscreenText
from direct.actor.Actor import Actor
import random
import sys
import os
import math

import models
import utils


camMax = 2.0
camMin = 0.0
camHeight = 1.0

WALL_HEIGHT = 3.2
SPEED_MOVE = 5
        
# Function to put instructions on the screen.
def addInstructions(pos, msg):
    return OnscreenText(text=msg, style=1, fg=(1, 1, 1, 1), scale=.05,
                        shadow=(0, 0, 0, 1), parent=base.a2dTopLeft,
                        pos=(0.08, -pos - 0.04), align=TextNode.ALeft)

# Function to put title on the screen.
def addTitle(text):
    return OnscreenText(text=text, style=1, fg=(1, 1, 1, 1), scale=.07,
                        parent=base.a2dBottomRight, align=TextNode.ARight,
                        pos=(-0.1, 0.09), shadow=(0, 0, 0, 1))


# would like to make the first two arguments a single context object.
def addCube(render, position, scale=1, rotate=1):
    # square0 = models.makeSquare(-1, -1, -1, 1, -1, 1)
    # square1 = models.makeSquare(-1, 1, -1, 1, 1, 1)
    # square2 = models.makeSquare(-1, 1, 1, 1, -1, 1)
    # square3 = models.makeSquare(-1, 1, -1, 1, -1, -1)
    # square4 = models.makeSquare(-1, -1, -1, -1, 1, 1)
    # square5 = models.makeSquare(1, -1, -1, 1, 1, 1)
    # snode = GeomNode('square')
    # snode.addGeom(square0)
    # snode.addGeom(square1)
    # snode.addGeom(square2)
    # snode.addGeom(square3)
    # snode.addGeom(square4)
    # snode.addGeom(square5)

    #cube = render.attachNewNode(snode)

    cn = CollisionNode('test')
    cn.addSolid(CollisionSphere(0, 0, 0, scale))
    cube = render.attachNewNode(cn)
    cube.show()
    cube.setScale(scale)

    #if rorate:
    #    cube.hprInterval(1.5, (360, 360, 360)).loop()
    
    # OpenGl by default only draws "front faces" (polygons whose vertices are
    # specified CCW).
    cube.setTwoSided(True)
    
    cube.setPos(position)
    
def addWall(render, position, l, w, h=WALL_HEIGHT, opaque=False):
    cn = CollisionNode('wall')
    cn.addSolid(CollisionBox((0,0,0),l,w,h))
    cube = render.attachNewNode(cn)
    cube.setTwoSided(True)
    cube.setPos(position)
    cube.setScale(1)

    if opaque:
        square0 = models.makeSquare(-1*l, -1*w, -1*h, l, -1*w, h) # back plane
        square1 = models.makeSquare(-1*l, 1*w, -1*h, l, 1*w, h) #
        square2 = models.makeSquare(-1*l, 1*w, h, l, -1*w, h)
        square3 = models.makeSquare(-1*l, 1*w, -1*h, l, -1*w, -1*h)
        square4 = models.makeSquare(-1*l, -1*w, -1*h, -1*l, 1*w, h)
        square5 = models.makeSquare(1*l, -1*w, -1*h, l, 1*w, h)
        snode = GeomNode('wall')
        snode.addGeom(square0)
        snode.addGeom(square1)
        snode.addGeom(square2)
        snode.addGeom(square3)
        snode.addGeom(square4)
        snode.addGeom(square5)
        cubewall = render.attachNewNode(snode)
        cubewall.setTwoSided(True)
        cubewall.setPos(position)
    else:
        cube.show()
    

def addDir(render, position, path='.'):
    #TODO for every file in a directory, make an item of relative size.
    entities = os.listdir(path)
    dirChild = []
    files = []
    
    for item in entities:
        if os.path.isdir(item):
            dirChild.append(item)
        else:
            files.append(item)

    lengthRoom = max(10, len(dirChild)*5)
    widthRoom = max(10, (len(files)*5)/(lengthRoom/5))
    print lengthRoom, widthRoom, len(files)
    #lengthRoom/=1.5
    #widthRoom/=1.5

    # Put up floor
    addWall(render, position-(0,0,WALL_HEIGHT), lengthRoom, widthRoom, 0.1, opaque=True)
    
    # Put up walls
    addWall(render, position + (0, widthRoom, 0), lengthRoom, 0.1, opaque=True)
    addWall(render, position - (0, widthRoom, 0), lengthRoom, 0.1, opaque=True)
    addWall(render, position + (lengthRoom, 0, 0), 0.1, widthRoom, opaque=True)
    addWall(render, position - (lengthRoom, 0, 0), 0.1, widthRoom, opaque=True)
    
    # Build door back to parent directory.
    # TODO
    # Build doors to child directories

    # Add representations of each file.
    lencross = widthRoom/5
    posFile = position + (-1*lengthRoom+2, -1*widthRoom+2, -0.5*WALL_HEIGHT)
    LETTER_SIZE = 0.035
    for i in range(len(files)):
        posNFile = posFile + (i%lencross*5,i/lencross*5,0)
        nfile = files[i]
        s = os.path.getsize(nfile)
        scl = utils.size_to_scale(s)
        addCube(render,  posNFile, scl)
        text = TextNode("filename: %s"%nfile)
        text.setText(nfile)
        textNodePath = render.attachNewNode(text)
        textNodePath.setPos(posNFile + (-1*len(nfile)*LETTER_SIZE, 0, scl*1.2))
        textNodePath.setScale(0.15)
        textNodePath.setTwoSided(True)
        
        
class RoamingRalphDemo(ShowBase):
    def __init__(self):
        # Set up the window, camera, etc.
        ShowBase.__init__(self)

        # Set the background color to black
        self.win.setClearColor((0, 0, 0, 1))

        # This is used to store which keys are currently pressed.
        self.keyMap = {
            "left": 0, "right": 0, "forward": 0, "back": 0, "cam-left": 0, "cam-right": 0}

        # Post the instructions
        self.title = addTitle(
            "Adventurer: 3rd Person File Manager (in progress)")
        self.inst1 = addInstructions(0.06, "[ESC]: Quit")
        self.inst2 = addInstructions(0.12, "[Arrows]: Angle Camera")
        self.inst3 = addInstructions(0.18, "[WASD]: Move")
        # Set up the environment
        #
        # This environment model contains collision meshes.  If you look
        # in the egg file, you will see the following:
        #
        #    <Collide> { Polyset keep descend }
        #
        # This tag causes the following mesh to be converted to a collision
        # mesh -- a mesh which is optimized for collision, not rendering.
        # It also keeps the original mesh, so there are now two copies ---
        # one optimized for rendering, one for collisions.

        #self.environ = loader.loadModel("models/world")
        #self.environ.reparentTo(render)

        #loader.unload_model
        startPos = Point3(0,0,0)#self.environ.find("**/start_point").getPos()
        
        # Setup controls
        self.keys = {}
        for key in ['arrow_left', 'arrow_right', 'arrow_up', 'arrow_down',
                    'a', 'd', 'w', 's']:
            self.keys[key] = 0
            self.accept(key, self.push_key, [key, 1])
            self.accept('shift-%s' % key, self.push_key, [key, 1])
            self.accept('%s-up' % key, self.push_key, [key, 0])
        #self.accept('f', self.toggleWireframe)
        #self.accept('x', self.toggle_xray_mode)
        #self.accept('b', self.toggle_model_bounds)
        self.accept('escape', __import__('sys').exit, [0])
        self.disableMouse()

        taskMgr.add(self.update, "moveTask")

        #insert test features
        #addCube(models, render, startPos + (0, 1, 0.5), 0.5)
        #addWall(models, render, startPos + (0, 1, 0.5), 30, 0.2)
        addDir(render, startPos + (0, 1, 0.5))
        
        # Game state variables
        self.isMoving = False

        # Set up the camera
        self.disableMouse()
        lens = PerspectiveLens()
        lens.setFov(60)
        lens.setNear(0.01)
        lens.setFar(1000.0)
        self.cam.node().setLens(lens)
        self.camera.setPos(startPos)
        self.heading = -95.0
        self.pitch = 0.0

        # Add collision to keept he camera in the room
        cn = CollisionNode('camera')
        cn.addSolid(CollisionSphere(0, 0, 0, 0.5))
        camColl = self.camera.attachNewNode(cn)
        self.cTrav = CollisionTraverser('camera traverser')
        self.camGroundHandler = CollisionHandlerPusher()
        self.camGroundHandler.addCollider(camColl, NodePath(self.camera))
        self.cTrav.addCollider(camColl, self.camGroundHandler)

        # Makes colliding objects show up 
        self.cTrav.showCollisions(render)
        
        # Create some lighting
        ambientLight = AmbientLight("ambientLight")
        ambientLight.setColor((.3, .3, .3, 1))
        directionalLight = DirectionalLight("directionalLight")
        directionalLight.setDirection((-5, -5, -5))
        directionalLight.setColor((1, 1, 1, 1))
        directionalLight.setSpecularColor((1, 1, 1, 1))
        render.setLight(render.attachNewNode(ambientLight))
        render.setLight(render.attachNewNode(directionalLight))


    def push_key(self, key, value):
        """Stores a value associated with a key."""
        self.keys[key] = value

    def update(self, task):
        """Updates the camera based on the keyboard input. Once this is
        done, then the CellManager's update function is called."""
        posStart = self.camera.getPos()
        delta = globalClock.getDt()
        move_x = delta * SPEED_MOVE * -self.keys['a'] + delta * SPEED_MOVE * self.keys['d']
        move_z = delta * SPEED_MOVE * self.keys['s'] + delta * SPEED_MOVE * -self.keys['w']
        self.camera.setHpr(self.heading, 0, 0)
        self.camera.setPos(self.camera, move_x, -move_z, 0)
        self.heading += (delta * 90 * self.keys['arrow_left'] +
                         delta * 90 * -self.keys['arrow_right'])
        self.pitch += (delta * 90 * self.keys['arrow_up'] +
                       delta * 90 * -self.keys['arrow_down'])
        self.camera.setHpr(self.heading, self.pitch, 0)

        # for entry in self.camGroundHandler.getEntries():
        #     if entry.getFromNode().getName() == "camera":
        #         print "Collision", posStart, self.camera.getPos()
        #         self.camera.setPos(posStart)
        #         break
        
        return task.cont

demo = RoamingRalphDemo()
demo.run()
