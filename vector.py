import math
import random

from singleton import *

# A kick-ass 2D vector class.
class Vector(object):
    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    def __add__(self, v):
        return Vector(self.x + v.x, self.y + v.y)

    def __sub__(self, v):
        return Vector(self.x - v.x, self.y - v.y)

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __abs__(self):
        return Vector(abs(self.x), abs(self.y))
    
    def __mul__(self, c):
        return Vector(c*self.x, c*self.y)

    def __rmul__(self, c):
        return Vector(c * self.x, c * self.y)

    def __div__(self, c):
        return Vector(self.x/c, self.y/c)

    def __rdiv__(self, c):
        return Vector(c/self.x, c/self.y)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return self.x != other.x or self.y != other.y

    def __repr__(self):
        return "<%.2f, %.2f>" % self.get_tuple()
    def __str__(self):
        return self.__repr__()

    @property
    def x(self):
        return self.__x
    @property
    def y(self):
        return self.__y

    @property
    def r(self):
        return self.__x
    @property
    def theta(self):
        return self.__y

    def get_x(self):
        return self.__x
    def get_y(self):
        return self.__y

    def get_r(self):
        return self.__x
    def get_theta(self):
        return self.__y

    def get_tuple(self):
        return (self.x, self.y)
    def get_int_tuple(self):
        return (int(self.x), int(self.y))

    def get_magnitude(self):
        squared = self.get_magnitude_squared()
        return math.sqrt(squared)
    def get_magnitude_squared(self):
        return self.x**2 + self.y**2

    def get_normal(self, magnitude=1):
        return magnitude * self/self.get_magnitude()
    def get_orthogonal(self):
        return Vector(-self.y, self.x)
    def get_components(self, v):
        tangent = v * Vector.dot_product(self, v)
        normal = self - tangent
        return normal, tangent

    @staticmethod
    def get_random():
        theta = random.uniform(0, 2 * math.pi)
        return Vector(math.cos(theta), math.sin(theta))

    @staticmethod
    def get_angle(A, B):
        temp = A.get_magnitude() * B.get_magnitude()
        temp = Vector.dot(A, B) / temp
        return math.acos(temp)

    @staticmethod
    def get_distance(A, B):
        return (A - B).get_magnitude()

    @staticmethod
    def get_manhattan(A, B):
        disp = B - A
        return abs(disp.x) + abs(disp.y)

    @staticmethod
    def dot_product(A, B):
        return A.x * B.x + A.y * B.y

    @staticmethod
    def perp_product(A, B):
        return A.x * B.y - A.y * B.x

    dot = dot_product
    perp = perp_product

@singleton
class ZeroVector(Vector):
    def __init__(self):
        Vector.__init__(self, 0, 0)

