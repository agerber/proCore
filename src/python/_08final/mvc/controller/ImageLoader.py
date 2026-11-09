import os
import traceback

from PIL import Image


# TODO PATTERN 7 of 10 (second instance): FACADE. ImageLoader hides PIL's Image.open, path resolution and the
# directory walk behind a single lookup, IMAGES[name]. See SoundLoader for the first instance.
#
# TODO PATTERN 8 of 10: FLYWEIGHT. Every PNG is decoded exactly once, when the singleton is constructed, and stored in
# IMAGES; every sprite that needs an image shares the same PIL Image object. A hundred WhiteCloudDebris explosions hold a
# hundred small dicts of references, not a hundred copies of nine decoded images. The image is the *intrinsic*
# (shared, immutable) state; center, orientation and radius are the *extrinsic* state each sprite keeps for itself and
# passes to renderRaster(). Sharing is safe only because nobody mutates the shared images; PIL's rotate() and resize()
# return new images, which is what makes the sharing work.
class ImageLoader:
    __instance = None
    IMAGES = {}

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super(ImageLoader, cls).__new__(cls)
            return cls.__instance
        raise Exception(" one instance of ImageLoader is already created ")

    def __init__(self):
        from mvc.controller.CommandCenter import CommandCenter
        rootDirectory = CommandCenter.getInstance().img
        localMap = {}
        try:
            localMap = self.loadPngImages(rootDirectory)
        except Exception:
            print(traceback.format_exc())

        self.IMAGES = localMap

    @staticmethod
    def getInstance():
        # this is now a singleton
        if (ImageLoader.__instance is None):
            ImageLoader.__instance = ImageLoader()

        return ImageLoader.__instance

    @staticmethod
    def loadPngImages(rootDirectory):
        pngImages = {}
        dirs = os.listdir(rootDirectory)

        for dir in dirs:
            if dir.startswith('.'):
                continue
            currentPath = os.path.join(rootDirectory, dir)
            files = os.listdir(currentPath)
            for file in files:
                # Ignore hidden files

                splitText = os.path.splitext(file)
                if splitText[1] == '.png' and 'do_not_load' not in splitText[0]:
                    # print(os.path.join(currentPath,file))
                    pngImages[splitText[0]] = ImageLoader.loadGraphic(os.path.join(currentPath, file))

        return pngImages

    @staticmethod
    def loadGraphic(imagePath: str) -> Image.Image:
        try:
            bufferedImage = Image.open(imagePath)
        except IOError as e:
            raise Exception(f"Cannot open image: {imagePath}")
        return bufferedImage