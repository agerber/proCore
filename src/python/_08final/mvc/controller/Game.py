import os
import sys

# Allow running this file directly (`python mvc/controller/Game.py`) by putting
# the package root (_08final/) on sys.path so the `mvc` package resolves.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pygame

from mvc.model.Movable import Movable
from mvc.model.Asteroid import Asteroid
from mvc.model.Nuke import Nuke
from mvc.model.NukeFloater import NukeFloater
from mvc.model.ShieldFloater import ShieldFloater
#from pythonic.mvc.model.prime.Dimension import Dimension
from mvc.view.GamePanel import GamePanel
from mvc.controller.CommandCenter import CommandCenter
from mvc.model.Falcon import Falcon, TurnState
from mvc.model.Bullet import Bullet
from mvc.controller.GameOp import GameOp
from mvc.model.prime.Dimension import Dimension
from mvc.model.prime.Point import Point
from mvc.controller.SoundLoader import SoundLoader

# in the Environmental Variables of the runtime configuration:
# WIDTH=980;HEIGHT=600 or something like this.
def _setDimFromEnv():
    try:
        width = int(os.getenv("WIDTH"))
        height = int(os.getenv("HEIGHT"))
        return Dimension(width, height)
    except (TypeError, ValueError):
        # some default value
        return Dimension(1200, 700)


# todo: refactor the code so that its in python style, and clean-up
class Game:
    # ===============================================
    # FIELDS
    # ===============================================

    # The dimension of the game-screen. Computed from env at class-definition (import)
    # time so DIM is populated even when this file is loaded under two names: as
    # __main__ (when run directly) AND as mvc.controller.Game (imported by the models).
    DIM = _setDimFromEnv()

    ANIMATION_DELAY = 40  # milliseconds between frames
    FRAMES_PER_SECOND = 1000 // ANIMATION_DELAY

    # points awarded for clearing a level (scaled by the level number)
    LEVEL_CLEAR_BONUS = 10_000

    # key-codes (pygame key constants)
    PAUSE = pygame.K_p  # p key
    QUIT = pygame.K_q  # q key
    LEFT = pygame.K_LEFT  # rotate left; left arrow
    RIGHT = pygame.K_RIGHT  # rotate right; right arrow
    UP = pygame.K_UP  # thrust; up arrow
    START = pygame.K_s  # s key
    FIRE = pygame.K_SPACE  # space key
    MUTE = pygame.K_m  # m-key mute
    NUKE = pygame.K_f  # f-key
    RADAR = pygame.K_a
    SMART = pygame.K_v

    # for possible future use
    # HYPER = 68 # D key
    # ALIEN = 65 # A key
    # SPECIAL = 70 # fire special weapon;  F key

    # ===============================================
    # ==CONSTRUCTOR
    # ===============================================

    def __init__(self):
        # DIM is computed once at class-definition time (see Game.DIM above), so there is no
        # need to reassign it here; it is already available before CommandCenter spawns sprites.
        # one-shot pygame/mixer bootstrap; needs CommandCenter constructed first.
        CommandCenter.getInstance()
        SoundLoader.init()
        self.gamePanel = GamePanel(Game.DIM)

    @staticmethod
    def setDimFromEnv():
        return _setDimFromEnv()

    def checkCollisions(self):

        cc = CommandCenter.getInstance()
        # this has an order of growth of O(FRIENDS * FOES)
        for movFriend in cc.movFriends:
            for movFoe in cc.movFoes:
                pntFriendCenter = movFriend.getCenter()
                pntFoeCenter = movFoe.getCenter()
                radFriend = movFriend.getRadius()
                radFoe = movFoe.getRadius()
                if pntFriendCenter.distance(pntFoeCenter) < (radFoe + radFriend):
                    cc.opsQueue.enqueue(movFriend, GameOp.Action.REMOVE)
                    cc.opsQueue.enqueue(movFoe, GameOp.Action.REMOVE)

        pntFalcon = cc.falcon.center
        radFalcon = cc.falcon.getRadius()
        # this has an order of growth of O(FLOATERS)
        for movFloater in cc.movFloaters:
            pntFloaterCenter = movFloater.getCenter()
            radFloater = movFloater.getRadius()
            if (pntFalcon.distance(pntFloaterCenter) < (radFalcon + radFloater)):
                cc.opsQueue.enqueue(movFloater, GameOp.Action.REMOVE)

    def processGameOpsQueue(self):
        # deferred mutation: these operations are done AFTER we have completed our collision detection to avoid
        # mutating the movable linkedlists while iterating them above.
        cc = CommandCenter.getInstance()
        while not cc.opsQueue.isEmpty():
            gameOp = cc.opsQueue.dequeue()
            mov = gameOp.movable

            list = None
            if mov.getTeam() == Movable.Team.FOE:
                list = cc.movFoes
            elif mov.getTeam() == Movable.Team.FRIEND:
                list = cc.movFriends
            elif mov.getTeam() == Movable.Team.FLOATER:
                list = cc.movFloaters
            else: # mov.getTeam() == Movable.Team.DEBRIS:
                list = cc.movDebris

            # the following block executes the callbacks
            action = gameOp.action
            if action == GameOp.Action.ADD:
                mov.addToGame(list)
            else:
                mov.removeFromGame(list)

    # The frame loop is driven by pygame: poll input events, advance and
    # draw one frame, then sleep to cap the rate at FRAMES_PER_SECOND.
    def main(self):
        # start the theme music
        SoundLoader.playSound("dr_loop.wav")
        CommandCenter.getInstance().isMuted = False

        clock = pygame.time.Clock()
        gameFrame = self.gamePanel.gameFrame

        while gameFrame.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameFrame.running = False
                elif event.type == pygame.KEYDOWN:
                    self.keyPressed(event.key)
                elif event.type == pygame.KEYUP:
                    self.keyReleased(event.key)

            if not gameFrame.running:
                break

            try:
                self.gamePanel.update()
                self.checkCollisions()
                self.checkNewLevel()
                self.checkFloaters()
                self.processGameOpsQueue()
            except Exception as e:
                import traceback
                print("Animation loop error:", e)
                traceback.print_exc()
                break

            clock.tick(Game.FRAMES_PER_SECOND)

        pygame.quit()

    def checkNewLevel(self):

        if not self.isLevelClear(): return

        cc = CommandCenter.getInstance()
        # currentLevel will be zero at beginning of game
        level = cc.level
        # award some points for having cleared the previous level
        cc.score += Game.LEVEL_CLEAR_BONUS * level

        # recenter the falcon at level clears
        cc.falcon.center = Point(int(round(Game.DIM.width / 2.0)), int(round(Game.DIM.height / 2.0)))

        # bump the level up
        level += 1
        cc.level = level

        # spawn some big new asteroids
        self.spawnBigAsteroids(level)
        # make falcon invincible momentarily in case new asteroids spawn on top of him
        if (cc.falcon.shield < Falcon.INITIAL_SPAWN_TIME):
            cc.falcon.shield = Falcon.INITIAL_SPAWN_TIME

        # show "Level: [X] UNIVERSE" in middle of screen
        cc.falcon.showLevel = Falcon.INITIAL_SPAWN_TIME

    def isLevelClear(self):
        asteroidFree = True
        for movFoe in CommandCenter.getInstance().movFoes:
            if isinstance(movFoe, Asteroid):
                asteroidFree = False
                break
        return asteroidFree

    def spawnBigAsteroids(self, num):
        cc = CommandCenter.getInstance()
        while num > 0:
            cc.opsQueue.enqueue(Asteroid(0), GameOp.Action.ADD)
            num -= 1

    def checkFloaters(self):
        self.spawnShieldFloater()
        self.spawnNukeFloater()

    def spawnNukeFloater(self):
        cc = CommandCenter.getInstance()
        if cc.frame % NukeFloater.SPAWN_NUKE_FLOATER == 0:
            cc.opsQueue.enqueue(NukeFloater(), GameOp.Action.ADD)

    def spawnShieldFloater(self):
        cc = CommandCenter.getInstance()
        if cc.frame % ShieldFloater.SPAWN_SHIELD_FLOATER == 0:
            cc.opsQueue.enqueue(ShieldFloater(), GameOp.Action.ADD)

    def stopLoopingSounds(self, *sounds):
        [sound.stop() for sound in sounds if hasattr(sound, "stop")]

    def keyPressed(self, keyCode):
        cc = CommandCenter.getInstance()
        falcon = cc.falcon
        # print(keyCode)
        if keyCode == Game.START and cc.isGameOver():
            cc.initGame()
            return
        if keyCode == Game.PAUSE:
            cc.isPaused = not cc.isPaused
        elif keyCode == Game.QUIT:
            self.gamePanel.gameFrame.running = False
        elif keyCode == Game.UP:
            falcon.thrusting = True
            SoundLoader.playSound("whitenoise_loop.wav")
        elif keyCode == Game.LEFT:
            falcon.turnState = TurnState.LEFT
        elif keyCode == Game.RIGHT:
            falcon.turnState = TurnState.RIGHT

    def keyReleased(self, keyCode):
        cc = CommandCenter.getInstance()
        falcon = cc.falcon
        if keyCode == Game.FIRE:
            cc.opsQueue.enqueue(Bullet(falcon), GameOp.Action.ADD)
        elif keyCode == Game.NUKE:
            cc.opsQueue.enqueue(Nuke(falcon), GameOp.Action.ADD)
        elif keyCode == Game.RIGHT or keyCode == Game.LEFT:
            falcon.turnState = TurnState.IDLE
        elif keyCode == Game.UP:
            falcon.thrusting = False
            SoundLoader.stopSound("whitenoise_loop.wav")

        elif keyCode == Game.SMART:
            cc.killAllFoes()

        elif keyCode == Game.MUTE:
            if not cc.isMuted:
                SoundLoader.stopSound("dr_loop.wav")
                cc.isMuted = True
            else:
                SoundLoader.playSound("dr_loop.wav")
                cc.isMuted = False

        elif keyCode == Game.RADAR:
            cc.isRadar = not cc.isRadar

if __name__ == "__main__":
    game = Game()
    game.main()