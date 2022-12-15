import pygame as pg
from .asset_handler import AssetHandler

global CHUNKSIZE, TILESIZE, GRAVITY, DECAY
TILESIZE = 12
CHUNKSIZE = 12 * TILESIZE
GRAVITY = 1.5
DECAY = 0.2


def chunkify(*coord):
    return tuple( [int(i // CHUNKSIZE) for i in coord] )


def dechunkify(*coord):
    return tuple( [int(i * CHUNKSIZE) for i in coord] )


class Chunk:
    def __init__(self, g, x: int=0, y: int=0):
        self.g = g
        self.x = x
        self.y = y
        self.tiles = []
        self.entities = []
        self.lights = []

    @property
    def coord(self) -> tuple[int, int]:
        return self.x, self.y

    @coord.setter 
    def coord(self, new):
        self.x, self.y = new

    def update(self, d_time=1.0):
        buffer = self.entities.copy()
        self.entities.clear()

        for t in self.tiles:
            t.update(d_time=d_time)
        for e in buffer:
            e.update(d_time=d_time)

        buffer = self.lights.copy()
        self.lights.clear()
        for l in buffer:
            l.update(d_time=d_time)

        del buffer

    def feed(self, code: str, data: dict):
        for e in self.entities:
            e.listen(code, data)

    def spawn(self):
        for t in self.tiles:
            if hasattr(t, 'spawn'): t.spawn()


class Light(object):
    def __init__(self, id, g):
        self.id = id
        self.g = g
        self.x = 0
        self.y = 0
        self.r = 0
        self.color = (185, 185, 185, 27)
        self.lifetime = -1
        self.parent = None

    def update(self, d_time=1.0):
        chunk = chunkify(*self.pos)

        if self.lifetime != -1:
            self.lifetime -= d_time
            if self.lifetime <= 0:
                del self
                return
        self.g.world.get_chunk(*chunk).lights.append(self)

    def draw(self, surf, scroll):
        pg.draw.circle(surf, self.color, (self.pos[0] - scroll[0], self.pos[1] - scroll[1]), self.r)

    @property
    def pos(self):
        x, y = self.x, self.y
        if self.relative:
            x += self.parent.rect.centerx
            y += self.parent.rect.centery
        return x, y

    @property
    def relative(self):
        return bool(self.parent)


class Entity(pg.sprite.Sprite):
    _EMPTY_ANIM = AssetHandler.get_anim('')
    def __init__(self, id, g) -> None:
        super(Entity, self).__init__()
        self.id = id
        self.g = g
        self.x = 0.0
        self.y = 0.0
        self.anim = self._EMPTY_ANIM
        self.vel = [0.0, 0.0]
        self.collides = True
        self.flipped = False
        self.grav_mod = 1.0
        self.listeners = {}

    def update(self, d_time=1.0) -> None:
        center = self.center
        if self.anim.update(d_time=d_time): self.anim.set_anim('def')
        self.center = center

        self.x += self.vel[0]
        self._collision(x=True)
        self.vel[0] -= self.vel[0] * DECAY
        self._gravity(d_time=d_time)
        self.y += self.vel[1]
        self._collision(y=True)
        self.vel[1] -= self.vel[1] * DECAY
        if self.vel[0] < 0: self.flipped = True
        if self.vel[0] > 0: self.flipped = False

        new_chunk = chunkify(*self.center)
        self.g.world.get_chunk(*new_chunk).entities.append(self)

    def listen(self, code: str, data: dict):
        pass

    def _collision(self, x=False, y=False):
        pass

    def _gravity(self, d_time=1.0):
        pass

    def create_light(self, rel_x, rel_y, r, color=(185, 185, 185, 27), life=120):
        d = { 'parent': self, 'x': rel_x, 'y': rel_y, 'r': r, 'color': color, 'lifetime': life }
        self.g.world.create_entity(Light, **d)

    @property
    def img(self) -> pg.Surface:
        return AssetHandler.get_drawn(*self.anim.draw_result, int(self.flipped))

    @property
    def mask(self) -> pg.mask.Mask:
        return AssetHandler.get_mask(*self.anim.draw_result, int(self.flipped))

    @property
    def pos(self) -> tuple[int or float, int or float]:
        return self.x, self.y

    @pos.setter
    def pos(self, new: list or tuple) -> None:
        self.x, self.y = new

    @property
    def center(self) -> tuple[int or float, int or float]:
        return self.x + (self.w/2), self.y + (self.h/2)

    @center.setter
    def center(self, new: list or tuple) -> None:
        self.x = new[0] - (self.w/2)
        self.y = new[1] - (self.h/2)

    @property
    def size(self) -> tuple[int, int]:
        return self.img.get_size()

    @property
    def w(self) -> int:
        return self.img.get_width()

    @property
    def h(self) -> int:
        return self.img.get_height()

    @property
    def rect(self) -> pg.Rect:
        return pg.Rect(self.pos, self.size)

    @property
    def direction(self) -> int:
        if self.flipped: return -1
        return 1


class Tile(Entity):
    def __init__(self, id, g):
        super(Tile, self).__init__(id, g)
        del self.vel
        self.chunk = None

        self.collides = True
        self.flipped = False

    def update(self, d_time=1.0):
        self.anim.update(d_time=d_time)

    @property
    def pos(self):
        return dechunkify(self.chunk.x)[0] + (self.x * TILESIZE), dechunkify(self.chunk.y)[0] + (self.y * TILESIZE)

    @pos.setter
    def pos(self, new):
        pass

    @property
    def center(self):
        return self.pos[0] + (self.size[0] / 2), self.pos[1] + (self.size[1] / 2)

    @center.setter
    def center(self, new):
        pass
