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
        return ((cood_1[0] - cood_2[0]) ** 2 + (cood_1[1] - cood_2[1]) ** 2)**0.5
