import pygame as pg


class Camera:
    def __init__(self, g, res: tuple):
        self.g = g
        self.size = res
        self.true_x = 0.0
        self.true_y = 0.0
        self.target_obj = None
        self.target_pos = None
        self.move_behavior = None

    @property
    def rect(self):
        return pg.Rect(self.true_x, self.true_y, self.size[0], self.size[1])

    @property
    def true_scroll(self):
        return [self.true_x, self.true_y]

    @true_scroll.setter
    def true_scroll(self, pos):
        self.true_x = pos[0]
        self.true_y = pos[1]

    @property
    def scroll(self):
        return int(self.true_x + (self.size[0]/2)), int(self.true_y + (self.size[1]/2))

    @scroll.setter
    def scroll(self, pos):
        self.true_x = pos[0] - (self.size[0]/2)
        self.true_y = pos[1] - (self.size[1]/2)

    def apply_scroll(self, pos):
        return int(pos[0] - self.true_x), int(pos[1] - self.true_y)

    def remove_scroll(self, pos):
        return pos[0] + self.true_x, pos[1] + self.true_y

    def update(self, d_time=1.0):
        t = (self.size[0]/2, self.size[1]/2)
        if self.target_pos:
            t = self.target_pos
        elif self.target_obj:
            t = self.target_obj.center
        if self.move_behavior:
            self.move_behavior(self, t, d_time)
        else:
            self.scroll = t

    def smooth(self, t, d_time=1.0):
        x, y = self.scroll
        x -= ((x - t[0]) / 12) * d_time
        y -= ((y - t[1]) / 12) * d_time
        self.scroll = (x, y)