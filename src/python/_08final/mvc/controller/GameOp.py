from enum import Enum
from dataclasses import dataclass

from mvc.model.Movable import Movable


# The GameOp (short for Game Operation) associates a movable with an action. Once the
# GameOpsQueue is processed it will add/remove movables from their appropriate list in the
# CommandCenter depending on the movable's team. Modelled as an immutable record (frozen dataclass).
@dataclass(frozen=True)
class GameOp:

    class Action(Enum):
        ADD = 1
        REMOVE = 2

    movable: Movable
    action: Action
