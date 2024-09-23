import random


class Verification:
    def __init__(self):
        self.code = 0

    def get_code(self):
        self.code = random.randint(100, 999)
        return self.code

    def check(self, code):
        return self.code == code
