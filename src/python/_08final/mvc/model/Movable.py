from enum import Enum
from abc import ABC, abstractmethod

from mvc.model.prime.Point import Point

# NOTE Movable is NOT the Facade design pattern, although it is often mislabeled as such. A Facade is one class that
# puts a simple front door on a complicated subsystem (SoundLoader and ImageLoader are the real Facades here). Movable
# is the model's *contract*: the seven operations the engine needs from anything in the game space. The controller and
# the view program to this ABC and never to Falcon or Asteroid. In Python the ABC is a choice, not a necessity: a
# typing.Protocol would state the same contract structurally, and a class could satisfy it without inheriting at all.

class Movable(ABC):

    class Team(Enum):
        FRIEND = 0
        FOE = 1
        FLOATER = 2
        DEBRIS = 3

    # for movables to move and draw themselves. See GamePanel class.
    @abstractmethod
    def move(self):
        pass

    @abstractmethod
    def draw(self, g):
        pass


    # for collision detection
    @abstractmethod
    def getRadius(self) -> int:
        pass

    @abstractmethod
    def getTeam(self) -> Team:
        pass

    @abstractmethod
    def getCenter(self) -> Point:
        pass


    # NOTE addToGame() and removeFromGame() are lifecycle callbacks, also called HOOK METHODS, and they are NOT the
    # Observer pattern (nothing subscribes to them; Game calls them on exactly one object when it drains the ops
    # queue). Sprite supplies the default (add/remove self from the list); subclasses override the hook to add a side
    # effect at that moment of the object's life: Bullet plays a sound on add, Asteroid spawns smaller asteroids and
    # awards points on remove, Nuke refuses to be removed before it expires. Hooks are the variable steps of the
    # TEMPLATE METHOD that processGameOpsQueue() implements; see Sprite for the pattern annotation.


    # lifecycle callbacks when a movable object is added or removed from the game-space. This is your opportunity
    # to add sounds or other side effects.
    @abstractmethod
    def addToGame(self, list):
        pass


    @abstractmethod
    def removeFromGame(self, list):
        pass


