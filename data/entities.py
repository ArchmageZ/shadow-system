import pygame as pg
from .containers import *


class Spawner(Tile):
    def __init__(self, id, g):
        super().__init__(id, g)

        self.entity = {}
        self.spawn_offset = (0, 0)

    def spawn(self) -> Entity:
        ent = self.entity.copy()
        t = globals().get(ent.pop('t', ''), Entity)
        if 'anim' in ent: ent['anim'] = AssetHandler.get_anim(ent['anim'])
        ent['x'] = self.rect.centerx + self.spawn_offset[0]
        ent['y'] = self.rect.centery + self.spawn_offset[1]
        e = self.g.world.create_entity(t, **ent)
        return e


class PhysicsEntity(Entity):
    def __init__(self, id, g) -> None:
        super().__init__(id, g)
        self.on_ground = False

    def _collision(self, x=False, y=False):
        collision_list = self.g.world.collision_list
        col_ind = self.rect.collidelist( [o.rect for o in collision_list] )
        if x:
            if col_ind == -1:  # SIMPLE PROJECTION CHECK TO ENSURE NO CLIPPING THROUGH OBJECTS AT HIGH SPEEDS
                p1, p2 = (self.center[0] - self.vel[0], self.center[1]), self.center
                for i, o in enumerate(collision_list):
                    if len(o.rect.clipline(p1, p2)) > 0:
                        col_ind = i

            if col_ind != -1 and collision_list[col_ind] is not self:
                o = collision_list[col_ind]
                if self.vel[0] > 0:
                    self.x = o.rect.left - self.w
                if self.vel[0] < 0:
                    self.x = o.rect.right
                self.vel[0] = 0.0
        if y:
            if col_ind == -1:  # SIMPLE PROJECTION CHECK TO ENSURE NO CLIPPING THROUGH OBJECTS AT HIGH SPEEDS
                p1, p2 = (self.center[0], self.center[1] - self.vel[1]), self.center
                for i, o in enumerate(collision_list):
                    if len(o.rect.clipline(p1, p2)) > 0:
                        col_ind = i
            
            if col_ind != -1 and collision_list[col_ind] is not self:
                o = collision_list[col_ind]
                if self.vel[1] > 0:
                    self.y = o.rect.top - self.h
                    self.on_ground = True
                if self.vel[1] < 0:
                    self.y = o.rect.bottom
                self.vel[1] = 0.0

    def update(self, d_time=1) -> None:
        self.on_ground = False
        if abs(self.vel[0]) > 0.15 or abs(self.vel[1]) > 0.15: self.anim.set_anim('moving', False)
        super().update(d_time)


class Player(PhysicsEntity):

    def __init__(self, id: int, g):
        super(Player, self).__init__(id, g)
        self.g.camera.target_obj = self
        self.speed = [0.5, 0.5]

        self.listeners = {'move_left': (self.give_velocity, {'x': -1}),
                          'move_right': (self.give_velocity, {'x': 1}),
                          'move_up': (self.give_velocity, {'y': -1}),
                          'move_down': (self.give_velocity, {'y': 1})
                         }
        self.execute = {}

    def update(self, d_time=1) -> None:
        removal = []
        for code in self.execute:
            func, data = self.execute[code]
            res = func(**data)
            if data.get('once', False) and res: removal.append(code)
        for code in removal: self.execute.pop(code)

        super().update(d_time)

    def listen(self, code: str, data: dict):
        code, down = '.'.join(code.split('.')[:-1]), (code.split('.')[-1] == 'down')
        if code in self.listeners:
            if down:
                data.update( self.listeners[code][1] )
                self.execute.update( { code: (self.listeners[code][0], data) } )
            elif code in self.execute:
                self.execute.pop(code)

    def give_velocity(self, x: int=0, y: int=0, mod=int, **_):
        self.vel[0] += x * self.speed[0]
        self.vel[1] += y * self.speed[1]

