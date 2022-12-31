# Tyler Cobb
# ETGG 1803 Lab #8
# 04/24/2021

import vector
import math


class Matrix:

    def __init__(self, *args):
        self.num_cols = len(args[0])
        self.rows = []
        for i in args:
            if isinstance(i, vector.Vector) and len(i) == self.num_cols:
                v = i.copy()    # Copy each vector so Matrix rows are independent from pre-existing Vector objects
                self.rows.append(v)
            else:
                raise TypeError("All arguments must be vectors of the same dimension.")
        self.num_rows = len(self.rows)

    def copy(self):
        """
        Creates a new Matrix instance and populates it with the properties of the instance calling the function
        :return: A deep copy of the Matrix.
        """
        new_matrix_rows = self.rows[:]
        new_matrix = Matrix(*new_matrix_rows)
        return new_matrix

    def __str__(self):
        string = ""
        maxes = []
        for col in range(self.num_cols):
            # Find the longest number in each column
            maximum = 0
            max_val = 0
            for row in self.rows:
                if len(str(row[col])) > maximum:
                    maximum = len(str(row[col]))
                    max_val = row[col]
            maxes.append(max_val)
        for row in range(self.num_rows):
            if row == 0:
                string += "/ "
                for value in range(self.num_cols):   # Value INDEX
                    if self.rows[row][value] == maxes[value]:
                        # If the value being added to the matrix has the longest number of the column,
                        # only one space after is necessary for alignment
                        string += str(self.rows[row][value]) + " "
                    else:
                        # If not, the spaces required for column alignment are equal to the difference in length
                        # between the longest value of the column and the value
                        # Add one space in case the number is not the max but the same length as it
                        string += str(self.rows[row][value]) + " " * (len(str(maxes[value])) - len(str(self.rows[row][value])) + 1)
                string += "\\\n"
            elif row == len(self.rows) - 1:
                string += "\\ "
                for value in range(self.num_cols):
                    if self.rows[row][value] == maxes[value]:
                        string += str(self.rows[row][value]) + " "
                    else:
                        string += str(self.rows[row][value]) + " " * (len(str(maxes[value])) - len(str(self.rows[row][value])) + 1)
                string += "/"
            else:
                string += "| "
                for value in range(self.num_cols):
                    if self.rows[row][value] == maxes[value]:
                        string += str(self.rows[row][value]) + " "
                    else:
                        string += str(self.rows[row][value]) + " " * (len(str(maxes[value])) - len(str(self.rows[row][value])) + 1)
                string += "|\n"
        return string

    def __getitem__(self, location):
        """
        :param location: A row and a column index in the Matrix
        :return: The specified entry in the Matrix
        """
        if isinstance(location, tuple) and len(location) == 2:
            if isinstance(location[0], int) and isinstance(location[1], int):
                return self.rows[location[0]][location[1]]
            else:
                raise TypeError("Matrix entries can only be accessed with integer indices.")
        else:
            raise TypeError("Matrix entries are accessed with a tuple of integer indices in the form of (row, column).")

    def __setitem__(self, location, value):
        """
        :param location: A row and a column index in the Matrix
        :param value: A new value to replace the previous entry
        :return: No return. Changes the value at the index to the given value.
        """
        if isinstance(location[0], int) and isinstance(location[1], int):
            if isinstance(value, (int, float)):
                if abs(value) < 1 and abs(value) - 0.0000000001 < 0:    # Gets rid of -0.0's
                    value = 0
                self.rows[location[0]][location[1]] = float(value)
            else:
                raise TypeError("Entries can only be set to an integer or float value.")
        else:
            raise TypeError("Matrix entries can only be accessed with integer indices.")

    def get_row(self, row):
        """
        Returns one complete row of the matrix in Vector form
        :param row: The index of the row
        :return: The specified row in Vector form
        """
        return self.rows[row]

    def get_column(self, column):
        """
        Creates one complete column of the matrix in Vector form
        :param column: The index of the column
        :return: The specified column in Vector form
        """
        col_data = []
        for row in self.rows:
            col_data.append(row[column])
        col = vector.Vector(*col_data)
        return col

    def set_row(self, index, v):
        """
        Set a row in the matrix to a new row vector
        :param index: The index of the row
        :param v: The vector to replace the row
        :return: Nothing returned
        """
        v = v.copy()
        if isinstance(index, int) and isinstance(v, vector.Vector):
            if v.dim == self.num_cols:  # Vector has to have same number of columns as other rows
                self.rows[index] = v
            else:
                raise TypeError("The new vector cannot have a different dimension from the one it is replacing.")
        else:
            raise TypeError("Rows are set by (index, vector), with vector being a Vector object.")

    def set_column(self, index, v):
        """
        Set a column in the matrix to a new column vector
        :param index: The index of the column
        :param v: The vector to replace the column
        :return: Nothing returned
        """
        v = v.copy()
        if isinstance(index, int) and isinstance(v, vector.Vector):
            if v.dim == self.num_rows:  # The number of rows = the number of values in the column
                for i in range(self.num_cols):
                    self[(i, index)] = v[i]
            else:
                raise TypeError("The new vector cannot have a different dimension from the one it is replacing.")
        else:
            raise TypeError("Columns are set by (index, vector), with vector being a Vector object.")

    def __add__(self, other):
        """
        Add two matrices
        :param other: The matrix to the right of the operator
        :return The sum of the two matrices
        """
        if isinstance(other, Matrix):
            new_matrix = self.copy()
            if other.num_rows == self.num_rows and other.num_cols == self.num_cols:
                for row in range(self.num_rows):
                    v = self.get_row(row) + other.get_row(row)
                    new_matrix.set_row(row, v)
                return new_matrix
            else:
                raise ValueError("The two matrices must have the same dimensions to be added.")
        else:
            raise TypeError("Only a matrix can be added to another matrix.")

    def __sub__(self, other):
        """
        Subtract two matrices
        :param other: The matrix to the right of the operator
        :return: The difference between the two matrices
        """
        new_matrix = self + (-other)
        return new_matrix

    def __mul__(self, other):
        """
        Multiply a matrix and matrix or matrix and scalar
        :param other: The matrix or scalar to the right of the operator
        :return: The product of the matrix and the other
        """
        if isinstance(other, (int, float)):
            new_matrix = self.copy()
            for row in range(self.num_rows):
                v = self.rows[row] * other
                new_matrix.set_row(row, v)
            return new_matrix
        elif isinstance(other, Matrix):
            new_matrix_rows = []
            if self.num_cols == other.num_rows:
                for row in range(self.num_rows):
                    new_row = []
                    for column in range(other.num_cols):
                        new_row.append(vector.dot(self.rows[row], other.get_column(column)))
                    row_vector = vector.Vector(*new_row)
                    new_matrix_rows.append(row_vector)
                new_matrix = Matrix(*new_matrix_rows)
                return new_matrix
            else:
                raise ValueError("The right matrix must have the same number of rows as the left has columns for them to be multiplied.")
        elif isinstance(other, vector.Vector):
            # Turn the vector into a column vector within a Matrix object, then multiply as usual
            vm_rows = []
            for row in range(other.dim):
                new_row = vector.Vector(other[row])
                vm_rows.append(new_row)
            vm = Matrix(*vm_rows)
            return self * vm
        else:
            raise TypeError("Matrices can only be multiplied by scalars, vectors, or matrices.")

    def __rmul__(self, other):
        """
        Handles multiplication if the matrix is on the right of the operator
        :param other: The thing to the left of the operator
        :return: The product of the matrix and other
        """
        if isinstance(other, vector.Vector):
            # Converts the vector into a row vector within a Matrix and multiplies as usual
            vm = Matrix(other)
            return vm * self
        else:
            return self * other

    def __neg__(self):
        """
        Creates the same matrix with opposite values
        :return: The negated matrix
        """
        return self * -1

    def __eq__(self, other):
        """
        Checks whether two matrices are identical
        :param other: The other matrix
        :return: True or False
        """
        equal = False
        if isinstance(other, Matrix):
            if self.num_rows == other.num_rows and self.num_cols == other.num_cols:
                for row in range(self.num_rows):
                    for column in range(other.num_cols):
                        if self[(row, column)] == other[(row, column)]:
                            equal = True
                        else:
                            equal = False
                            return equal
                return equal
            else:
                return equal
        else:
            return equal

    def det(self):
        """
        Finds the determinant of the matrix if it is 2x2, 3x3, or 4x4
        :return: The determinant of the matrix
        """
        if self.num_rows == 2 and self.num_cols == 2:
            determinant = self[(0, 0)] * self[(1, 1)] - self[(0, 1)] * self[(1, 0)]
            return determinant
        elif self.num_rows == 3 and self.num_cols == 3:
            submatrix_1 = Matrix(vector.Vector(self[(1, 1)], self[(1, 2)]), vector.Vector(self[(2, 1)], self[(2, 2)]))
            submatrix_2 = Matrix(vector.Vector(self[(1, 0)], self[(1, 2)]), vector.Vector(self[(2, 0)], self[(2, 2)]))
            submatrix_3 = Matrix(vector.Vector(self[(1, 0)], self[(1, 1)]), vector.Vector(self[(2, 0)], self[(2, 1)]))
            determinant = self[(0, 0)] * submatrix_1.det() - self[(0, 1)] * submatrix_2.det() + self[(0, 2)] * submatrix_3.det()
            return determinant
        elif self.num_rows == 4 and self.num_cols == 4:
            submatrix_1 = Matrix(vector.Vector(self[(1, 1)], self[(1, 2)], self[(1, 3)]), vector.Vector(self[(2, 1)], self[(2, 2)], self[(2, 3)]), vector.Vector(self[(3, 1)], self[(3, 2)], self[(3, 3)]))
            submatrix_2 = Matrix(vector.Vector(self[(1, 0)], self[(1, 2)], self[(1, 3)]), vector.Vector(self[(2, 0)], self[(2, 2)], self[(2, 3)]), vector.Vector(self[(3, 0)], self[(3, 2)], self[(3, 3)]))
            submatrix_3 = Matrix(vector.Vector(self[(1, 0)], self[(1, 1)], self[(1, 3)]), vector.Vector(self[(2, 0)], self[(2, 1)], self[(2, 3)]), vector.Vector(self[(3, 0)], self[(3, 1)], self[(3, 3)]))
            submatrix_4 = Matrix(vector.Vector(self[(1, 0)], self[(1, 1)], self[(1, 2)]), vector.Vector(self[(2, 0)], self[(2, 1)], self[(2, 2)]), vector.Vector(self[(3, 0)], self[(3, 1)], self[(3, 2)]))
            determinant = self[(0, 0)] * submatrix_1.det() - self[(0, 1)] * submatrix_2.det() + self[(0, 2)] * submatrix_3.det() - self[(0, 3)] * submatrix_4.det()
            return determinant
        else:
            raise TypeError("Can only find determinants of 2x2, 3x3, and 4x4 matrices.")

    def transpose(self):
        """
        Finds the transpose of the matrix
        :return: The transpose of the matrix
        """
        if self.num_rows == self.num_cols:
            t = self.copy()
            # Swap columns and rows
            for row in range(self.num_rows):
                t.rows[row] = self.get_column(row)
        else:
            # Create a new matrix with adjusted dimensions and fill the rows with the columns of the original
            t_rows = []
            for col in range(self.num_cols):
                t_rows.append(self.get_column(col))
            t = Matrix(*t_rows)
        return t


def identity(dim):
    """
    Creates an identity matrix
    :param dim: The number of rows and columns in the identity matrix
    :return: The desired identity matrix
    """
    if isinstance(dim, int) and dim > 0:
        i_rows = []
        for row in range(dim):
            v_data = []
            for a in range(dim):
                v_data.append(0)    # Create a zero vector of the appropriate dimension
            v = vector.Vector(*v_data)
            v[row] = 1  # The value in the vector that corresponds to the row index should be 1
            i_rows.append(v)
        i = Matrix(*i_rows)
        return i
    else:
        raise TypeError("Enter the number of rows in the desired identity matrix. Must be integer and >0.")


def all_zeroes(rows, columns):
    """
    Creates a matrix of all zeroes
    :param rows: Row dimension of the matrix
    :param columns: Column dimension of the matrix
    :return: A matrix full of zeroes
    """
    if isinstance(rows, int) and rows > 0 and isinstance(columns, int) and columns > 0:
        z_rows = []
        for row in range(rows):
            v_data = []
            for a in range(columns):
                v_data.append(0)    # Create a zero vector of the appropriate dimension
            z_rows.append(vector.Vector(*v_data))
        z = Matrix(*z_rows)
        return z
    else:
        raise TypeError("Matrix is created by passing (rows, columns). Each must be integers and >0.")


def all_ones(rows, columns):
    """
    Creates a matrix of all ones
    :param rows: Row dimension of the matrix
    :param columns: Column dimension of the matrix
    :return: A matrix full of ones
    """
    if isinstance(rows, int) and rows > 0 and isinstance(columns, int) and columns > 0:
        o_rows = []
        for row in range(rows):
            v_data = []
            for a in range(columns):
                v_data.append(1)    # Create a vector full of ones of the appropriate dimension
            o_rows.append(vector.Vector(*v_data))
        o = Matrix(*o_rows)
        return o
    else:
        raise TypeError("Matrix is created by passing (rows, columns). Each must be integers and >0.")


def trace(matrix):
    """
    Finds the trace of a square matrix
    :param matrix: A square matrix
    :return: The trace of the matrix
    """
    if isinstance(matrix, Matrix):
        if matrix.num_rows == matrix.num_cols:
            sum = 0
            for row in range(matrix.num_rows):
                sum += matrix[(row, row)]   # Diagonal entries are found at (row index, row index)
            return sum
        else:
            raise ValueError("Matrix must be square to find its trace.")
    else:
        raise TypeError("Can only find the trace of square Matrix objects.")


def inverse(matrix):
    """
    Finds the inverse of a matrix
    :param matrix: A matrix
    :return: The inverse of the original matrix
    """
    if isinstance(matrix, Matrix) and matrix.num_rows == matrix.num_cols and 2 <= matrix.num_rows <= 4:
        if matrix.det() != 0:
            inv = matrix.copy()
            if matrix.num_rows == 2:
                inv[(0, 0)] = matrix[(1, 1)]
                inv[(0, 1)] *= -1
                inv[(1, 0)] *= -1
                inv[(1, 1)] = matrix[(0, 0)]
                for row in range(matrix.num_rows):
                    inv.rows[row] = inv.rows[row] * (1 / matrix.det())
                return inv
            elif matrix.num_rows == 3:
                for row in range(3):
                    # Find the row and column of each entry in each minor matrix
                    if row == 0:
                        target_row = 1
                        second_row = 2
                    elif row == 1:
                        target_row = 0
                        second_row = 2
                    else:
                        target_row = 0
                        second_row = 1
                    for col in range(3):
                        if col == 0:
                            target_col = 1
                            second_col = 2
                        elif col == 1:
                            target_col = 0
                            second_col = 2
                        else:
                            target_col = 0
                            second_col = 1
                        # Construct the minor matrices, find their determinants,
                        # and make those the corresponding entry in the matrix
                        minor = Matrix(vector.Vector(matrix[(target_row, target_col)], matrix[(target_row, second_col)]), vector.Vector(matrix[(second_row, target_col)], matrix[(second_row, second_col)]))
                        determinant = minor.det()
                        inv[(row, col)] = determinant
                # Create a matrix of cofactors
                for row in range(inv.num_rows):
                    for col in range(inv.num_cols):
                        inv[(row, col)] *= (-1) ** (row + 1 + (1 + col))
                inv = inv.transpose()   # Transpose the matrix
                inv *= 1 / matrix.det()     # Divide each term by the determinant of the original matrix
                return inv
            else:   # 4x4 inverse
                for row in range(4):
                    # Find the row and column of each entry in each minor matrix
                    if row == 0:
                        target_row = 1
                    else:
                        target_row = 0
                    if row == 1:
                        second_row = target_row + 2
                    else:
                        second_row = target_row + 1
                    if row == 2:
                        third_row = second_row + 2
                    else:
                        third_row = second_row + 1
                    for col in range(4):
                        if col == 0:
                            target_col = 1
                        else:
                            target_col = 0
                        if col == 1:
                            second_col = target_col + 2
                        else:
                            second_col = target_col + 1
                        if col == 2:
                            third_col = second_col + 2
                        else:
                            third_col = second_col + 1
                        # Construct the minor matrices, find their determinants,
                        # and make those the corresponding entry in the matrix
                        r1 = vector.Vector(matrix[(target_row, target_col)], matrix[(target_row, second_col)],
                                           matrix[(target_row, third_col)])
                        r2 = vector.Vector(matrix[(second_row, target_col)], matrix[(second_row, second_col)],
                                           matrix[(second_row, third_col)])
                        r3 = vector.Vector(matrix[(third_row, target_col)], matrix[(third_row, second_col)],
                                           matrix[(third_row, third_col)])
                        minor = Matrix(r1, r2, r3)
                        determinant = minor.det()
                        inv[(row, col)] = determinant
                # Create a matrix of cofactors
                for row in range(inv.num_rows):
                    for col in range(inv.num_cols):
                        inv[(row, col)] *= (-1) ** (row + 1 + (1 + col))
                inv = inv.transpose()   # Transpose the matrix
                inv *= 1 / matrix.det()     # Divide each term by the determinant of the original matrix
                return inv
        else:
            raise ValueError("This matrix has no inverse.")
    else:
        raise TypeError("This function can only find the inverse of 2x2, 3x3, or 4x4 matrices.")


def rotate(angle):
    """
    Creates a 2D rotation matrix based on the provided angle. Counter-clockwise direction.
    :param angle: The angle of rotation in degrees
    :return: A rotation matrix
    """
    if isinstance(angle, (int, float)):
        rad_angle = math.radians(angle)
        v1 = vector.Vector(math.cos(rad_angle), math.sin(rad_angle) * -1)
        v2 = vector.Vector(math.sin(rad_angle), math.cos(rad_angle))
        r = Matrix(v1, v2)
        return r
    else:
        raise TypeError("Must enter an angle in degrees.")


def hg(object):
    """
    Converts either a Vector or Matrix into homogenous coordinates
    :param object: A Vector or Matrix object
    :return: The object in homogenous form
    """
    if isinstance(object, vector.Vector):
        h = vector.Vector(*object.data, 1)
    elif isinstance(object, Matrix):
        h_rows = []
        for row in range(len(object.rows)):
            h_row = vector.Vector(*object.get_row(row).data, 1)
            h_rows.append(h_row)
        h = Matrix(*h_rows)
    else:
        raise TypeError("Only Vectors or Matrices can be converted to homogenous coordinates.")
    return h


def translate(dimension, *args):
    """
    Creates a matrix that will translate another matrix
    :param dimension: The homogenized dimension of the matrix to be translated
    :param args: The desired translations, in order of x_movement, y_movement, z_movement, and so on
    :return: The translation matrix
    """
    keep_going = False
    if isinstance(dimension, int) and dimension > 0:
        for value in args:
            if isinstance(value, (int, float)):
                keep_going = True
            else:
                raise TypeError("Can only translate a matrix by integer or float values.")
    else:
        raise TypeError("Dimension for translation must be an integer and >0.")
    if keep_going:
        tr = identity(dimension)
        for i in range(len(args)):
            tr[(dimension - 1, i)] = args[i]    # Bottom row index is equal to dimension - 1
        return tr


def project(dimension):
    """
    Create a matrix to project another matrix
    :param dimension: The desired dimension to project onto
    :return: The projection matrix
    """
    if isinstance(dimension, int) and dimension > 1:
        p_rows = []
        temp_i = identity(dimension)    # Part of the projection matrix is an identity matrix.
        for row in temp_i.rows:
            p_rows.append(row)
        last_row_data = []  # The last row is all zeroes.
        for columns in range(dimension):
            last_row_data.append(0)
        last_row = vector.Vector(*last_row_data)
        p_rows.append(last_row)
        p = Matrix(*p_rows)
        return p

