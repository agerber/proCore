
from mvc.controller.CommandCenter import CommandCenter
from mvc.controller.SoundLoader import SoundLoader
from mvc.model.Falcon import Falcon
from mvc.model.Floater import Floater
from mvc.model.prime.Color import Color


class NukeFloater(Floater):
    # spawn every 14 seconds (in java Game.FRAMES_PER_SECOND * 12)
    SPAWN_NUKE_FLOATER = 350
    # frames before this floater expires of natural mortality
    EXPIRY = 350

    def __init__(self):
        super().__init__()
        #yellow
        self.color = Color.YELLOW
        self.expiry = NukeFloater.EXPIRY



    def removeFromGame(self, list):
        super().removeFromGame(list)
        # if expiry > 0, then this remove was the result of a collision w/Falcon, and not natural mortality.
        if (self.expiry > 0):
            CommandCenter.getInstance().falcon.nukeMeter = Falcon.MAX_NUKE
            SoundLoader.playSound("nuke-up.wav")