import os
from dataclasses import dataclass
from typing import Optional


from mvc.controller.GameOpsQueue import GameOpsQueue
from mvc.controller.GameOp import GameOp
from mvc.model.prime.Dimension import Dimension
from mvc.model.prime.LinkedList import LinkedList

import sys


class CommandCenter:
    __instance = None

    # the following code ensures that you can only call the constructor ONCE
    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(CommandCenter, cls).__new__(cls)
            return cls.__instance
        raise Exception(" one instance of CommandCenter is already created ")

    def __init__(self):
        # Imported here (not at module top) to break the import cycle with
        # Falcon/Radar — both reference CommandCenter for runtime state.
        from mvc.model.Falcon import Falcon
        from mvc.model.Radar import Radar

        self.numFalcons = 0
        self.level = 0
        self.score = 0
        self.isPaused = False
        self.isMuted = True
        self.frame = 0
        self.isRadar = False
        self.universes = [
            Universe("FREE FLY", Dimension(1, 1)),
            Universe("CENTER", Dimension(1, 1)),
            Universe("BIG", Dimension(3, 3)),
            Universe("HORIZONTAL", Dimension(3, 1)),
            Universe("VERTICAL", Dimension(1, 3)),
            Universe("DARK", Dimension(4, 4)),
        ]


        # Anchor resource paths to the repo's shared resources dir, not the CWD,
        # so the game runs from any working directory. From this file
        # (src/python/_08final/mvc/controller/) the resources live four levels
        # up at src/resources/.
        basePath = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "resources")
        )
        self.snd = os.path.join(basePath, "sounds") + os.path.sep
        self.img = os.path.join(basePath, "imgs") + os.path.sep

        self.falcon = Falcon()
        self.radar = Radar()

        # NOTE These four lists are NOT the Composite design pattern, although they are often mislabeled as such.
        # In Composite, the container is itself a Component (a LinkedList of Movables would have to *be* a Movable, with
        # its own move() and draw(), so a group of sprites could be treated as one sprite). These are plain polymorphic
        # collections: each holds heterogeneous Movables (Falcon, Bullet, Asteroid, Star ...) and the engine calls
        # move()/draw() on each without knowing its class. In Python that is duck typing plus the ABC, not a pattern.

        self.movDebris = LinkedList()
        self.movFriends = LinkedList()
        self.movFoes = LinkedList()
        self.movFloaters = LinkedList()

        self.falconCentered = True
        self.opsQueue = GameOpsQueue()
        self.diffX = 0
        self.diffY = 0


    # TODO PATTERN 1 of 10: SINGLETON. CommandCenter holds the game's aggregate state (score, level, the team lists,
    # the ops queue), so the class guarantees one instance: __new__ above refuses to create a second object, the sole
    # instance lives in the private class attribute __instance, and getInstance() is the global access point that
    # creates it lazily. ImageLoader uses the same __new__ idiom. The idiomatic Python alternative is simply a module:
    # a module is imported once, cached in sys.modules, and its globals are a singleton for free. See Chapter 44.

    @staticmethod
    def getInstance():
        # this is now a singleton
        if (CommandCenter.__instance is None):
            CommandCenter.__instance = CommandCenter()

        return CommandCenter.__instance

    def initGame(self):
        self.clearAll()
        self.level = 0
        self.score = 0
        self.isPaused = False
        self.isRadar = True
        self.numFalcons = 4
        self.generateStarField()
        self.opsQueue.enqueue(self.falcon, GameOp.Action.ADD)
        self.opsQueue.enqueue(self.radar, GameOp.Action.ADD)

        self.falcon.decrementFalconNumAndSpawn()

    def killAllFoes(self):
        for mov in self.movFoes:
            self.opsQueue.enqueue(mov, GameOp.Action.REMOVE)


    def clearAll(self):
        self.movDebris.clear()
        self.movFriends.clear()
        self.movFoes.clear()
        self.movFloaters.clear()

    def generateStarField(self):
        from mvc.model.Star import Star
        count = 100
        while (count > 0):
            self.opsQueue.enqueue(Star(), GameOp.Action.ADD)
            count -= 1

    def incrementFrame(self):
        # use of ternary expression to simplify the logic to one line
        self.frame = self.frame + 1 if self.frame < sys.maxsize else 0

    def isGameOver(self) -> bool:  # //if the number of falcons is zero, then game over
        return self.numFalcons < 1

    def isFalconPositionFixed(self):
        uni = self.optUni()
        return True if uni is None else uni.name.upper() != "FREE FLY"

    def optUni(self) -> Optional["Universe"]:
        if self.level == 0:
            return None
        index = (self.level - 1) % len(self.universes)
        return self.universes[index]

    def getUniDim(self):
        uni = self.optUni()
        return Dimension(1, 1) if uni is None else uni.dimension

    def getUniName(self):
        uni = self.optUni()
        return "" if uni is None else uni.name


# record associating a universe name with its dimension (as a multiple of the game screen)
@dataclass(frozen=True)
class Universe:
    name: str
    dimension: Dimension

