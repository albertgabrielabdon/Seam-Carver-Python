#!/usr/bin/env python3

from math import sqrt
from xml.dom.minidom import ReadOnlySequentialNamedNodeMap
from picture import Picture


class SeamCarver(Picture):
    def energy(self, i: int, j: int) -> float:
        '''
        Return the energy of pixel at column i and row j
        '''
        if i < 0 or j < 0 or i >= self.width() or j >= self.height():
            raise IndexError("Pixel index out of bounds")
        
        border_conditions = (i == 0 or j == 0 or i+1 == self.width() or j+1 == self.height())

        previous_x = self[(i-1 + self.width()) % self.width(), j] if border_conditions else self[i-1, j] #wrap around     
        next_x = self[(i+1) % self.width(), j] if border_conditions else self[i+1, j]
        
        previous_y = self[i, (j-1 + self.height()) % self.height()] if border_conditions else self[i, j-1] #wrap around
        next_y = self[i, (j+1) % self.height()] if border_conditions else self[i, j+1]

        delta_x = sum((next_x[i] - previous_x[i])**2 for i in range(3))
        delta_y = sum((next_y[i] - previous_y[i])**2 for i in range(3))

        energy = sqrt(delta_x + delta_y)
        
        return energy

    def find_vertical_seam(self, is_horizontal=False) -> list[int]:
        '''
        Return a sequence of indices representing the lowest-energy
        vertical seam
        '''
        width = self.width()
        height = self.height()

        matrix = [[0 for i in range(width)] for j in range(height)]

        for row in range(0, height):
            for col in range(width):
                if row == 0:
                    matrix[0][col] = self.energy(col, 0)
                else:
                    if col == 0:
                        min_above = min(matrix[row-1][col], matrix[row-1][col+1])
                        matrix[row][col] = self.energy(col, row) + min_above
                    elif col == (width-1):
                        min_above = min(matrix[row-1][col-1], matrix[row-1][col])
                        matrix[row][col] = self.energy(col, row) + min_above
                    else:
                        min_above = min(matrix[row-1][col-1], matrix[row-1][col], matrix[row-1][col+1])
                        matrix[row][col] = self.energy(col, row) + min_above

        min_energy_value = 1e20
        seam = [-1]
        col = 0

        for i in range(width):
            if matrix[height-1][i] <= min_energy_value:
                min_energy_value = matrix[height-1][i]
                seam[0] = i

        for row in range(height-1, 0, -1):
            col = seam[0]

            if col == 0:
                min_above = min(matrix[row-1][col], matrix[row-1][col+1])
                if min_above == matrix[row-1][col]:
                    seam.insert(0, col)
                else:
                    seam.insert(0, col+1)

            elif col == (width-1):
                min_above = min(matrix[row-1][col-1], matrix[row-1][col])
                if min_above == matrix[row-1][col-1]:
                    seam.insert(0, col-1)
                else:
                    seam.insert(0, col)
            
            else:
                min_above = min(matrix[row-1][col-1], matrix[row-1][col], matrix[row-1][col+1])
                if min_above == matrix[row-1][col-1]:
                    seam.insert(0, col-1)
                elif min_above == matrix[row-1][col]:
                    seam.insert(0, col)
                else:
                    seam.insert(0, col+1)

        return seam

    def find_horizontal_seam(self) -> list[int]:
        '''
        Return a sequence of indices representing the lowest-energy
        horizontal seam
        '''
        #https://pythonexamples.org/python-pillow-rotate-image-90-180-270-degrees/

        rotated = SeamCarver(self.picture().rotate(90, expand = True))
        seam = rotated.find_vertical_seam()
        seam.reverse()
        rotated.picture().rotate(-90, expand=True)
        return seam

    def remove_vertical_seam(self, seam: list[int]):
        '''
        Remove a vertical seam from the picture
        '''
        if self._width <= 1 or len(seam) != self._height:
            raise SeamError
        
        for col in range(len(seam) - 1):
            if abs(seam[col] - seam[col+1]) > 1: raise SeamError

        width = self.width()
        height = self.height()

        if len(seam) != height or width == 1:
            raise SeamError
            
        for row in range(height):
            for col in range(seam[row], width - 1):
                self[col, row] = self[col+1, row]

        self._width -= 1
                
        for row in range(height):
            del self[self._width, row]

            
    def remove_horizontal_seam(self, seam: list[int]):
        '''
        Remove a vertical seam from the picture
        '''
        if len(seam) != self._width or self._height <= 1:
            raise SeamError

        for row in range(len(seam) - 1):
            if abs(seam[row] - seam[row+1]) > 1:
                raise SeamError

        self.transpose()
        self.remove_vertical_seam(seam)
        self.transpose()
        return

    def transpose(self):
        '''
        transpose the image
        '''
        transposed_image = {
            (row, col): self[col, row]
            for col in range(self._width)
            for row in range(self._height)
        }

        self.clear()

        for (row, col), value in transposed_image.items():
            self[row, col] = value

        self._width, self._height = self._height, self._width
        return



class SeamError(Exception):
    pass
