import random

from mvc.model.prime.Point import Point
from mvc.model.prime.Color import Color
from mvc.model.Movable import Movable
from mvc.controller.CommandCenter import CommandCenter


class Star(Movable):

    def __init__(self):
        from mvc.controller.Game import Game
        # center is some random point in the game space
        self.center = Point(random.randint(0, Game.DIM.width), random.randint(0, Game.DIM.height))
        bright = random.randint(0, 225)
        self.color = Color.fromRGB(bright, bright, bright)  # some gray value. stars are muted from 0-225 / 255

    def move(self):
        from mvc.controller.Game import Game
        if not CommandCenter.getInstance().isFalconPositionFixed():  return
            # right-bounds reached
        if self.center.x > Game.DIM.width:
            self.center.x = 1
            # left-bounds reached
        elif self.center.x < 0:
            self.center.x = Game.DIM.width - 1
            # bottom-bounds reached
        elif self.center.y > Game.DIM.height:
            self.center.y = 1
            # top-bounds reached
        elif self.center.y < 0:
            self.center.y = Game.DIM.height - 1
            # in-bounds
        else:
            # move star in opposite direction of falcon
            newXPos = self.center.x - CommandCenter.getInstance().falcon.deltaX
            newYPos = self.center.y - CommandCenter.getInstance().falcon.deltaY
            self.center.x = int(round(newXPos))
            self.center.y =  int(round(newYPos))

    def draw(self, g):
        g.setColor(self.color)
        g.drawOval(self.center.x, self.center.y, self.getRadius(), self.getRadius())

    def getRadius(self) -> int:
        return 1

    def getTeam(self) -> Movable.Team:
        return Movable.Team.DEBRIS

    def getCenter(self) -> Point:
        return self.center

    def addToGame(self, list):
        list.add(self)

    def removeFromGame(self, list):
        list.remove(self)
