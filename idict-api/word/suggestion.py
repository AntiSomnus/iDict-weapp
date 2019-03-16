from weighted_levenshtein import lev, dam_lev, osa
import numpy as np


class KeyboardUtil:
    keyboard_array = [
        ['q', ' ', 'w', ' ', 'e', ' ', 'r', ' ', 't', ' ', 'y', ' ', 'u', ' ', 'i', ' ', 'o', ' ', 'p'],
        [' ', 'a', ' ', 's', ' ', 'd', ' ', 'f', ' ', 'g', ' ', 'h', ' ', 'j', ' ', 'k', ' ', 'l', ' '],
        [' ', ' ', ' ', 'z', ' ', 'x', ' ', 'c', ' ', 'v', ' ', 'b', ' ', 'n', ' ', 'm', ' ', ' ', ' '],
    ]

    @staticmethod
    def get_coordinate(char: str):
        for (index, line) in enumerate(KeyboardUtil.keyboard_array):
            if char in line:
                return index, line.index(char)

    @staticmethod
    def get_distance(char_1: str, char_2: str):
        cood_1 = KeyboardUtil.get_coordinate(char_1)
        cood_2 = KeyboardUtil.get_coordinate(char_2)
        return ((cood_1[0] - cood_2[0]) ** 2 + (cood_1[1] - cood_2[1]) ** 2) ** 0.5


class Suggestion:
    def __init__(self):
        self.substitute_costs = np.ones((128, 128), dtype=np.float64)  # make a 2D array of 1's
        self.insert_costs = np.full(128, 2.4)
        self.delete_costs = np.full(128, 3.0)
        self.transpose_costs = np.ones((128, 128), dtype=np.float64)
        letters = 'abcdefghijklmnopqrstuvwxyz'
        for char_1 in letters:
            for char_2 in letters:
                self.substitute_costs[ord(char_1), ord(char_2)] = \
                    KeyboardUtil.get_distance(char_1, char_2)

    def get_cost(self, word_1: str, word_2: str):
        return osa(word_1.lower(), word_2.lower(),
                   transpose_costs=self.transpose_costs,
                   substitute_costs=self.substitute_costs,
                   insert_costs=self.insert_costs,
                   delete_costs=self.delete_costs,
                   )


