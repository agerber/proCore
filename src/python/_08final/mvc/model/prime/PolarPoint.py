from dataclasses import dataclass


# this record (immutable dataclass) is used in conjunction with Point to render vector graphics.
# r corresponds to the hypotenuse in cartesian (0.0-1.0); theta is in radians (0.0-2*Pi).
@dataclass(frozen=True)
class PolarPoint:
    r: float
    theta: float
