# Tyler Cobb
# ETGG 1803 Lab #6
# 03/12/2021
# Outside Resources:
# https://stackabuse.com/variable-length-arguments-in-python-with-args-and-kwargs/
# https://www.youtube.com/watch?v=PfmfECXmR88
# https://www.geeksforgeeks.org/getter-and-setter-in-python/
# https://stackoverflow.com/questions/46698824/python-deep-copy-without-using-copy-module
# 3D Math Primer for Graphics and Game Development, 2nd Edition

import math


class Vector:

    def __init__(self, *args):
        """
        :param args: Accepts a variable amount of components for the vector
        """
        self.data = []
        for i in args:
            if isinstance(i, (int, float)):
                self.data.append(float(i))
            else:
                raise TypeError("Only integer or float values are accepted.")
        self.dim = len(self.data)
        if self.dim == 2:
            self.__class__ = Vector2
        if self.dim == 3:
            self.__class__ = Vector3

    def __str__(self):
        """
        :return: A string that provides the type of Vector and it's components
        """
        string = "<Vector" + str(self.dim) + ": "
        for i in range(len(self.data)):
            if i < len(self.data) - 1:
                string += str((self[i])) + ", "
            elif i == len(self.data) - 1:
                string += str(float((self[i])))
        string += ">"
        return string

    def __len__(self):
        """
        :return: Returns the number of components that the Vector has
        """
        return self.dim

    def __getitem__(self, index):
        """
        :param index: An integer index
        :return: The float value located at the index
        """
        if isinstance(index, int):
            return float(self.data[index])
        else:
            raise TypeError("Values are only located at integer indices.")

    def __setitem__(self, index, value):
        """
        :param index: An integer index
        :param value: A new value.
        :return: No return. Changes the value at the index to the given value.
        """
        if isinstance(value, (int, float)):
            self.data[index] = float(value)
        else:
            raise TypeError("Only integer or float values are accepted.")

    def __eq__(self, other):
        """
        Determines whether two vectors are equivalent.
        :param other: Another Vector.
        :return: Whether or not the vectors are equivalent.
        """
        equal = False
        if isinstance(other, Vector):
            if self.dim == other.dim:
                for i in range(len(self.data)):
                    if self[i] == other[i]:
                        equal = True
                    else:
                        # If one component is not equal to a corresponding component, the vectors are not equal
                        equal = False
                        return equal
            else:
                # If the two vectors have different dimensions, they are not equal
                return equal
        else:
            # If the vector is being compared to something that isn't a vector, they are not equal
            return equal
        # If the vectors pass all tests, the function with return true
        return equal

    def copy(self):
        """
        Creates a new Vector instance and populates it with the properties of the instance calling the function
        :return: A deep copy of the Vector.
        """
        new_vector_data = self.data[:]
        new_vector = Vector(*new_vector_data)
        return new_vector

    def __mul__(self, other):
        """
        Multiplication between a vector on the left and a scalar on the right
        :param other: A scalar
        :return: A vector with the newly multiplied values
        """
        if isinstance(other, (int, float)):
            new_data = []
            for i in range(len(self.data)):
                new_data.append(self[i] * other)
            new_vector = Vector(*new_data)
            return new_vector
        else:
            return NotImplemented

    def __rmul__(self, other):
        """
        Multiplication between a scalar on the left and a vector on the right
        :param other: A scalar
        :return: A vector with the newly multiplied values
        """
        return self.__mul__(other)

    def __add__(self, other):
        """
        Adds two vectors
        :param other: Another vector
        :return: A vector that is the sum of both
        """
        if isinstance(other, Vector):
            new_data = []
            for i in range(len(self.data)):
                new_data.append(self[i] + other[i])
            new_vector = Vector(*new_data)
            return new_vector
        else:
            raise TypeError(
                f"You can only add another {self.__class__.__name__} to this {self.__class__.__name__} (You passed '{other}'.)")

    def __sub__(self, other):
        """
        Subtracts two vectors
        :param other: Another vector
        :return: A vector that is the difference of the two
        """
        if isinstance(other, Vector):
            new_data = []
            for i in range(len(self.data)):
                new_data.append(self[i] - other[i])
            new_vector = Vector(*new_data)
            return new_vector
        else:
            raise TypeError(
                f"You can only subtract another {self.__class__.__name__} from this {self.__class__.__name__} (You passed '{other}'.)")

    def __neg__(self):
        """
        Negates the vector
        :return: The opposite vector of this instance
        """
        return self * -1

    def __truediv__(self, other):
        """
        Divides a vector by a scalar
        :param other: A scalar
        :return: A vector that is the quotient of itself divided by other
        """
        if isinstance(other, (int, float)) and other != 0:
            new_data = []
            for i in range(len(self.data)):
                new_data.append(self[i] / other)
            new_vector = Vector(*new_data)
            return new_vector
        elif other == 0:
            raise ValueError("Can't divide by 0.")
        else:
            raise TypeError("Vectors are only divisible by scalar values")

    def norm(self, p):
        """
        Finds the p-norm of the vector.
        :param p: A positive integer or the string "infinity".
        :return: The corresponding p-norm.
        """
        if isinstance(p, int):
            if p >= 0:
                sum = 0
                for i in range(len(self.data)):
                    sum += abs(self[i]) ** p
                if p > 0:
                    return sum ** (1 / p)
                else:   # If p == 0, the norm is equivalent to the sum
                    return sum
            else:
                raise ValueError("p must be a positive value that is greater than 0.")
        elif isinstance(p, str):
            if p == "infinity":
                abs_data = []
                for i in range(len(self.data)):
                    abs_data.append(abs(self.data[i]))
                return max(abs_data)
            else:
                raise ValueError('This function can only accept a positive integer or string input "infinity"')
        else:
            raise TypeError('This function can only accept a positive integer or string input "infinity"')

    @property
    def mag(self):
        """
        Finds the length of the vector.
        :return: The 2-norm of the vector.
        """
        return self.norm(2)

    @property
    def mag_squared(self):
        """
        Finds the length of the vector squared.
        :return: The square of the 2-norm
        """
        return dot(self, self)

    @property
    def normalize(self):
        """
        Returns a unit vector in the direction of this Vector.
        """
        return self / self.mag

    @property
    def is_zero(self):
        """
        Determine if the Vector is the zero Vector of it's dimension
        :return: True if the Vector is the zero Vector of the appropriate dimension, False, otherwise
        """
        result = False
        for i in range(len(self.data)):
            if self.data[i] == 0:
                result = True
            else:
                # If one component in the Vector does not equal zero,
                # it is not a zero vector and the result can be returned
                result = False
                return result
        return result

    @property
    def i(self):
        """
        Returns a tuple of the coordinates of the Vector, converted to integers.
        """
        coords = ()
        for i in range(len(self.data)):
            coords += (int(self.data[i]),)
        return coords


class Vector2(Vector):
    def __init__(self, a, b):
        """
        :param a: x component of the vector
        :param b: y component of the vector
        :return: A vector instance that is both Vector and Vector2
        """
        super().__init__(a, b)

    @property
    def x(self):
        """
        self: A Vector2 instance
        :return: The x component
        """
        return self[0]

    @x.setter
    def x(self, a):
        """
        :param a: A new value
        :return: No return. Changes x component to the new value
        """
        if isinstance(a, (int, float)):
            self[0] = float(a)
        else:
            raise TypeError("Only integer or float values are accepted.")

    @property
    def y(self):
        """
        self: A Vector2 instance
        :return: The y component
        """
        return self[1]

    @y.setter
    def y(self, a):
        """
        :param a: A new value
        :return: No return. Changes y component to the new value.
        """
        if isinstance(a, (int, float)):
            self[1] = float(a)
        else:
            raise TypeError("Only integer or float values are accepted.")

    @property
    def degrees(self):
        """
        Convert the radian measure of the vector into degrees
        :return: The degree measure of the vector in polar space
        """
        return math.degrees(self.radians)

    @property
    def degrees_inv(self):
        """
        Negate the degree measure of the vector
        :return: The vector's degree measure using an inverted y-axis
        """
        return math.degrees(self.radians_inv)

    @property
    def radians(self):
        """
        Find the radian measure of the vector
        :return: The vector's angle in terms of radians
        """
        return math.atan2(self.y, self.x)

    @property
    def radians_inv(self):
        """
        Negate the radian measure of the vector
        :return: The vector's radian measure using an inverted y-axis
        """
        return math.atan2(-self.y, self.x)

    @property
    def perpendicular(self):
        """
        Creates a vector that is perpendicular to this vector
        :return: A Vector2 perpendicular to the original vector
        """
        return Vector(-self.y, self.x)


class Vector3(Vector):
    def __init__(self, a, b, c):
        """
        :param a: x component of the vector
        :param b: y component of the vector
        :param c: z component of the vector
        :return: A vector instance that is both Vector and Vector3
        """
        super().__init__(a, b, c)

    @property
    def x(self):
        """
        self: A Vector3 instance
        :return: The x component
        """
        return self[0]

    @x.setter
    def x(self, a):
        """
        :param a: A new value.
        :return: No return. Changes x component to the new value.
        """
        if isinstance(a, (int, float)):
            self[0] = float(a)
        else:
            raise TypeError("Only integer or float values are accepted.")

    @property
    def y(self):
        """
        self: A Vector3 instance
        :return: The y component
        """
        return self[1]

    @y.setter
    def y(self, a):
        """
        :param a: A new value.
        :return: No return. Changes y component to the new value.
        """
        if isinstance(a, (int, float)):
            self[1] = float(a)
        else:
            raise TypeError("Only integer or float values are accepted.")

    @property
    def z(self):
        """
        self: A Vector3 instance
        :return: The z component
        """
        return self[2]

    @z.setter
    def z(self, a):
        """
        :param a: A new value
        :return: No return. Changes z component to the new value.
        """
        if isinstance(a, (int, float)):
            self[2] = float(a)
        else:
            raise TypeError("Only integer or float values are accepted.")


def dot(a, b):
    """
    Finds the dot product of two vectors
    :param a: A vector
    :param b: Another vector
    :return: The dot product
    """
    if isinstance(a, Vector):
        if isinstance(b, Vector):
            if a.dim == b.dim:
                sum = 0
                for i in range(len(a.data)):
                    product = a[i] * b[i]
                    sum += product
                return sum
            else:
                raise TypeError("The two vectors must have the same dimensions.")
        else:
            raise TypeError("Input must both be vectors.")
    else:
        raise TypeError("Input must both be vectors.")


def cross(v, w):
    """
    Finds the cross product of two three-dimensional vectors
    :param v: A Vector3
    :param w: Another Vector3
    :return: The cross product of the two vectors
    """
    if isinstance(v, Vector3):
        if isinstance(w, Vector3):
            x = (v.y * w.z) - (v.z * w.y)
            y = (v.z * w.x) - (v.x * w.z)
            z = (v.x * w.y) - (v.y * w.x)
            return Vector(x, y, z)
        else:
            raise TypeError("Can only calculate a cross product if both vectors are three dimensional.")
    else:
        raise TypeError("Can only calculate a cross product if both vectors are three dimensional.")


def polar_to_Vector2(r, theta, inv=True):
    """
    Converts polar coordinates into a Vector2
    :param r: Distance from the origin
    :param theta: Degree angle of the vector
    :param inv: Whether or not to invert the y-axis
    :return: A vector that corresponds to the given polar coordinates.
    """
    if isinstance(r, (int, float)):
        if isinstance(theta, (int, float)):
            theta = math.radians(theta)  # The degree measure must be converted to radians to work with trig functions
            x = r * math.cos(theta)
            y = r * math.sin(theta)
            if inv:     # Defaulted to True for accuracy in pygame
                y = -y
            if abs(x) <= 0.000000001:     # Floating point zero fix
                x = 0
            if abs(y) <= 0.000000001:
                y = 0
        else:
            raise TypeError("Second parameter must be an int or float degree value.")
    else:
        raise TypeError("First parameter must be an int or float.")
    return Vector2(x, y)

