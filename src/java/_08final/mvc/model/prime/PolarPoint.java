package _08final.mvc.model.prime;

//this record is used in conjunction with Point[] for rendering vector graphics.
//r corresponds to the hypotenuse in cartesian, a number between 0.0 and 1.0.
//theta is degrees expressed in radians, a number between 0.0 and 6.283 (2 * Pi).
public record PolarPoint(double r, double theta) {
}
