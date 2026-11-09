import pygame


# TODO PATTERN 7 of 10: FACADE. pygame.mixer is a subsystem (init, channels, Sound objects, looping flags, a cache of
# one-shot effects). SoundLoader puts one simple front door on it: playSound(name) and stopSound(name). Callers such
# as Bullet and Game import nothing from pygame.mixer and never learn that looped and one-shot clips are handled
# differently. ImageLoader is the same pattern over PIL and the directory walk.
class SoundLoader:
    # static member
    soundDictionary = {}
    # one-shot sounds, loaded lazily and cached (keyed by filename)
    _oneShotCache = {}
    _initialized = False

    # Eager pygame/mixer setup is deferred out of the class body so that
    # importing this module no longer forces CommandCenter to construct.
    # Call SoundLoader.init() once at startup, after CommandCenter exists.
    @classmethod
    def init(cls):
        if cls._initialized:
            return
        from mvc.controller.CommandCenter import CommandCenter
        pygame.mixer.init()
        # give one-shot effects (explosions, bullets, spawns) room to overlap
        pygame.mixer.set_num_channels(32)
        snd = CommandCenter.getInstance().snd
        cls.soundDictionary = {
            "whitenoise_loop.wav": pygame.mixer.Sound(snd + "whitenoise_loop.wav"),
            "dr_loop.wav":          pygame.mixer.Sound(snd + "dr_loop.wav"),
        }
        cls._initialized = True

    @staticmethod
    def loopedCondition(strPath):
        return strPath.lower().endswith("_loop.wav")

    # Used for both looped and non-looped clips (mirrors Java SoundLoader.playSound).
    # Looped clips (suffixed _loop.wav) are fetched from the pre-loaded soundDictionary.
    # Non-looped one-shot effects are loaded lazily and cached; pygame.mixer.Sound.play()
    # is non-blocking and grabs a free channel on its own, so no thread pool is needed.
    @classmethod
    def playSound(cls, strPath):
        if cls.loopedCondition(strPath):
            clip = cls.soundDictionary.get(strPath)
            if clip is not None:
                clip.play(loops=-1)
            return
        from mvc.controller.CommandCenter import CommandCenter
        try:
            sound = cls._oneShotCache.get(strPath)
            if sound is None:
                sound = pygame.mixer.Sound(CommandCenter.getInstance().snd + strPath)
                cls._oneShotCache[strPath] = sound
            sound.play()
        except Exception:
            pass

    # Non-looped clips cannot be stopped, they simply expire on their own. Calling this
    # method on a non-looped clip will do nothing.
    @classmethod
    def stopSound(cls, strPath):
        if not cls.loopedCondition(strPath):
            return
        clip = cls.soundDictionary.get(strPath)
        if clip is not None:
            clip.stop()
