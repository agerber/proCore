from typing import List
import math

from mvc.model.prime.Point import Point
from mvc.model.prime.PolarPoint import PolarPoint
from functional import seq
from PIL import Image


class Utils:

    @staticmethod
    def cartesiansToPolars(pntCartesians: List[Point]) -> List[PolarPoint]:
        hypotenuseOfPoint = lambda pnt: math.sqrt(pnt.x ** 2 + pnt.y ** 2)
        # determine the largest hypotenuse
        LARGEST_HYP = max(map(hypotenuseOfPoint, pntCartesians), default=0.0)

        cartToPolarTransform = lambda pnt, dbl: PolarPoint(
            hypotenuseOfPoint(pnt) / dbl,
            math.degrees(math.atan2(pnt.y, pnt.x)) * math.pi / 180
        )

        return seq(pntCartesians) \
            .map(lambda pnt: cartToPolarTransform(pnt, LARGEST_HYP)) \
            .list()

    @staticmethod
    def transparent(img) -> Image:
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        transparentImg = Image.new("RGBA", img.size, (0, 0, 0, 0))
        # Paste the original image onto the transparent image
        transparentImg.paste(img, (0, 0), img)
        return transparentImg
