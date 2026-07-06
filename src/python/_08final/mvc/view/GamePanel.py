from typing import Tuple

from PIL import Image, ImageFont

from mvc.controller.CommandCenter import CommandCenter
from mvc.controller.Utils import Utils
from mvc.model.prime.PolarPoint import PolarPoint
from mvc.model.prime.Point import Point
from mvc.view.GameFrame import GameFrame
from mvc.view.Graphics import Graphics
from mvc.model.prime.Color import Color
from functional import seq
import math
import os


class GamePanel:
    # spacing (px) between the little ship icons that show remaining lives
    SHIP_ICON_SPACING = 27
    # distance (px) from the bottom of the screen for the HUD row (ship icons and meters)
    HUD_MARGIN_BOTTOM = 20

    def __init__(self, dim):

        baseDir = os.path.dirname(os.path.abspath(__file__))
        FONT_PATH = os.path.join(baseDir, "..", "..", "..", "..", "resources", "font", "OpenSans-Bold.ttf")
        self.fontNormal = ImageFont.truetype(FONT_PATH, 14)
        self.fontBig = ImageFont.truetype(FONT_PATH, 22)

        self.fontWidth = 0
        self.fontHeight = 0

        self.pntShipsRemaining = None
        self.gameFrame = GameFrame()

        self.pntShipsRemaining = []
        self.pntShipsRemaining.append(Point(0, 9))
        self.pntShipsRemaining.append(Point(-1, 6))
        self.pntShipsRemaining.append(Point(-1, 3))
        self.pntShipsRemaining.append(Point(-4, 1))
        self.pntShipsRemaining.append(Point(4, 1))
        self.pntShipsRemaining.append(Point(-4, 1))
        self.pntShipsRemaining.append(Point(-4, -2))
        self.pntShipsRemaining.append(Point(-1, -2))
        self.pntShipsRemaining.append(Point(-1, -9))
        self.pntShipsRemaining.append(Point(-1, -2))
        self.pntShipsRemaining.append(Point(-4, -2))
        self.pntShipsRemaining.append(Point(-10, -8))
        self.pntShipsRemaining.append(Point(-5, -9))
        self.pntShipsRemaining.append(Point(-7, -11))
        self.pntShipsRemaining.append(Point(-4, -11))
        self.pntShipsRemaining.append(Point(-2, -9))
        self.pntShipsRemaining.append(Point(-2, -10))
        self.pntShipsRemaining.append(Point(-1, -10))
        self.pntShipsRemaining.append(Point(-1, -9))
        self.pntShipsRemaining.append(Point(1, -9))
        self.pntShipsRemaining.append(Point(1, -10))
        self.pntShipsRemaining.append(Point(2, -10))
        self.pntShipsRemaining.append(Point(2, -9))
        self.pntShipsRemaining.append(Point(4, -11))
        self.pntShipsRemaining.append(Point(7, -11))
        self.pntShipsRemaining.append(Point(5, -9))
        self.pntShipsRemaining.append(Point(10, -8))
        self.pntShipsRemaining.append(Point(4, -2))
        self.pntShipsRemaining.append(Point(1, -2))
        self.pntShipsRemaining.append(Point(1, -9))
        self.pntShipsRemaining.append(Point(1, -2))
        self.pntShipsRemaining.append(Point(4, -2))
        self.pntShipsRemaining.append(Point(4, 1))
        self.pntShipsRemaining.append(Point(1, 3))
        self.pntShipsRemaining.append(Point(1, 6))
        self.pntShipsRemaining.append(Point(0, 9))

        self.gameFrame.setup(dim.width, dim.height, "Game Base")

    def drawFalconStatus(self, g):
        from mvc.controller.Game import Game
        OFFSET_LEFT = 220

        cc = CommandCenter.getInstance()
        falcon = cc.falcon

        # draw the level in the upper-right corner
        levelText = f"Level : [{cc.level}]  {cc.getUniName()}"

        g.setColor(Color.WHITE)
        g.setFont(self.fontNormal)
        g.drawString(levelText, Game.DIM.width - OFFSET_LEFT, 10)
        formattedScore = "{:,}".format(cc.score)
        g.drawString(f"Score: {formattedScore}", Game.DIM.width - OFFSET_LEFT, 30)


        statusArray = []

        if falcon.showLevel > 0:
            statusArray.append(levelText)

        if falcon.nukeMeter > 0:
            statusArray.append("Press 'F' for Nuke")

        if falcon.maxSpeedAttained:
            statusArray.append("WARNING - SLOW DOWN")

        # draw the statusArray strings to middle of screen. unpack the list to satisfy the var-args definition.
        if statusArray:
            self.displayTextOnScreen(g, *statusArray)

        # draw PYTHON VERSION and the frame number to bottom left screen
        g.drawString(f"FRAME[PYTHON]:{cc.frame}",
                     self.fontWidth + 10,
                     Game.DIM.height - (self.fontHeight + 22))

    # mirrors Java's GamePanel.update(Graphics g): creates an off-screen
    # double-buffer, draws into its Graphics context, then blits the
    # finished image to the on-screen tk Label in one swoop to avoid
    # flickering.
    def update(self):
        from mvc.controller.Game import Game

        imgOff = Image.new("RGB", (Game.DIM.width, Game.DIM.height), Color.BLACK)
        g = Graphics(imgOff)

        cc = CommandCenter.getInstance()
        cc.incrementFrame()

        if cc.isGameOver():
            self.displayTextOnScreen(g,
                                     "GAME OVER",
                                     "use the arrow keys to turn and thrust",
                                     "use the space bar to fire",
                                     "'S' to Start",
                                     "'P' to Pause",
                                     "'Q' to Quit",
                                     "'M' to toggle music",
                                     "'A' to toggle radar"
                                     )

        elif cc.isPaused:
            self.displayTextOnScreen(g, "Game Paused")
        else:
            self.moveDrawMovables(g,
                                  cc.movDebris,
                                  cc.movFloaters,
                                  cc.movFoes,
                                  cc.movFriends)

            self.drawMeters(g)
            self.drawFalconStatus(g)
            self.drawNumberShipsRemaining(g)

        # blit the finished off-screen image onto the screen in one swoop.
        self.gameFrame.blit(g.image)

    def drawNumberShipsRemaining(self, g):
        numFalcons = CommandCenter.getInstance().numFalcons
        while numFalcons > 1:
            self.drawOneShip(g, numFalcons)
            numFalcons -= 1

    def drawOneShip(self, g, offSet):
        from mvc.controller.Game import Game

        # rotate the ship 90 degrees
        DEGREES_90 = -90
        SHIP_RADIUS = 15
        X_POS = Game.DIM.width - (GamePanel.SHIP_ICON_SPACING * offSet)
        Y_POS = Game.DIM.height - GamePanel.HUD_MARGIN_BOTTOM

        # the reason we convert to polar-points is that it's much easier to rotate polar-points.
        polars = Utils.cartesiansToPolars(self.pntShipsRemaining)

        # 2: rotate raw polars given the orientation of the sprite.
        rotatePolarBy90 = lambda pp: PolarPoint(
            pp.r,
            pp.theta + math.radians(DEGREES_90)
        )

        # 3: convert the rotated polars back to cartesians
        polarToCartesian = lambda pp: Point(
            int(pp.r * SHIP_RADIUS * math.sin(pp.theta)),
            int(pp.r * SHIP_RADIUS * math.cos(pp.theta))
        )

        # 4: adjust the cartesians for the location (center-point) of the sprite.
        # the reason we subtract the y-value has to do with how python plots the vertical axis for
        # graphics (from top to bottom)
        adjustForLocation = lambda pnt: Point(
            X_POS + pnt.x,
            Y_POS - pnt.y
        )

        # 5: draw the polygon using the List of raw polars from above, applying mapping transforms as required

        g.setColor(Color.ORANGE)
        g.drawPolygon(
            seq(polars)\
                .map(rotatePolarBy90)\
                .map(polarToCartesian)\
                .map(adjustForLocation)\
                .map(lambda point: (point.x, point.y))\
                .list())


    def drawOneMeter(self, g, color: Tuple, offSet: int, percent: int):
        from mvc.controller.Game import Game
        xVal = Game.DIM.width - (100 + 120 * offSet)
        yVal = Game.DIM.height - GamePanel.HUD_MARGIN_BOTTOM

        g.setColor(color)
        g.fillRect(xVal, yVal, percent, 10)
        g.setColor(Color.GREY)
        g.drawRect(xVal, yVal, 100, 10)

    def drawMeters(self, g):

        falcon = CommandCenter.getInstance().falcon
        shieldValue = falcon.shield // 2
        nukeValue = falcon.nukeMeter // 6
        self.drawOneMeter(g, color=Color.CYAN, offSet=1, percent=shieldValue)
        self.drawOneMeter(g, color=Color.YELLOW, offSet=2, percent=nukeValue)

    def moveDrawMovables(self, g, *teams):
        for team in teams:
            for mov in team:
                mov.move()
                mov.draw(g)

    # var-args as lines
    def displayTextOnScreen(self, g, *lines):
        from mvc.controller.Game import Game
        g.setColor(Color.WHITE)
        g.setFont(self.fontNormal)
        yVal = 0
        for line in lines:
            g.drawString(line, Game.DIM.width // 2 - len(line) * 2.5 - 10, 200 + yVal)
            yVal += 40
