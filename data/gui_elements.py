import pygame as pg
from .asset_handler import AssetHandler
from . import text


class GUI:
    bounds_color = (225, 85, 85, 255)
    draw_bounds = False
    def __init__(self, g, offset:tuple[int, int]=(0, 0), size:tuple[int, int] or None=None, elements: list=[]) -> None:
        self.g = g
        self.active = True
        self.elements = elements
        for e in self.elements: e.parent = self
        self.offset = offset
        if size: self.w, self.h = size
        else:    self.w, self.h = self.g.display.RENDER_RES

    @property
    def rect(self) -> pg.Rect:
        return pg.Rect(self.offset[0], self.offset[1], self.size[0], self.size[1])

    @property
    def size(self) -> tuple[int, int]:
        return (self.w, self.h)

    def update(self, d_time=1.0) -> None:
        for e in self.elements:
            e.update(d_time=d_time)

    def draw(self, surf: pg.Surface) -> None:
        self.update(self.g.d_time)
        if self.draw_bounds: pg.draw.rect(surf, self.bounds_color, self.rect, 1)
        for e in self.elements:
            e.draw(surf, self.rect)
            if self.draw_bounds:
                r = pg.Rect(self.offset[0] + e.pos[0], self.offset[1] + e.pos[1], e.size[0], e.size[1])
                pg.draw.rect(surf, e.bounds_color, r, 1)

    def click(self, pos: tuple[float, float], code: str, data:dict={}) -> None:
        for e in self.elements:
            if e.rect.collidepoint(pos): e.clicked(code, data)

    def listen(self, code: str, data: dict) -> None:
        for e in self.elements:
            e.listen(code, data)


class GUIElement(object):
    bounds_color = (255, 0, 0, 255)
    def __init__(self, parent_ui: GUI or None=None) -> None:
        self.parent = parent_ui
        self.pos = (0, 0)
        self.w, self.h = (0, 0)
        self.listeners = dict()

    @property
    def rect(self) -> pg.Rect:
        return pg.Rect(self.parent.offset[0] + self.pos[0], self.parent.offset[1] + self.pos[1], *self.size)

    @property
    def size(self) -> tuple[int, int]:
        return self.w, self.h

    def update(self, d_time=1.0) -> None:
        pass

    def draw(self, surf: pg.Surface, bounds: pg.Rect) -> None:
        pass

    def listen(self, code: str, data: dict) -> None:
        if code in self.listeners:
            self.listeners[code](**data)

    def clicked(self, code: str, data: dict={}) -> None:
        pass

    def set_pos(self, x: int or float, y: int or float) -> None:
        self.pos = (x, y)


class GUIAnimatedElement(GUIElement):
    EMPTY_ANIM = AssetHandler.EMPTY_COLLECTION
    def __init__(self, parent_ui: GUI or None=None) -> None:
        super().__init__(parent_ui)
        self.anim = self.EMPTY_ANIM

    @property
    def image(self) -> pg.Surface:
        return AssetHandler.get_drawn(*self.anim.draw_result)

    @property
    def size(self) -> tuple[int, int]:
        return self.image.get_size()

    def update(self, d_time=1.0) -> None:
        self.anim.update(d_time=d_time)

    def draw(self, surf: pg.Surface, bounds:pg.Rect) -> None:
        surf.blit(self.image, self.rect, area=bounds)

    def change_anim(self, a_id: str or None=None) -> None:
        self.anim.set_anim(new=a_id)


class Cursor(GUIAnimatedElement):
    def __init__(self, parent_ui: GUI or None=None) -> None:
        super().__init__(parent_ui)
        self.anim = AssetHandler.get_anim('cursor')
        self.hot_spot = (0, 0)
        self.listeners.update( {'mouse.motion': self.set_pos,
                                'mouse1.down': self.change_anim, 'mouse3.down': self.change_anim} )

    @property
    def rect(self) -> pg.Rect:
        r = super().rect
        r.top -= self.hot_spot[1]
        r.left -= self.hot_spot[0]
        return r

    def update(self, d_time=1) -> None:
        super().update(d_time)

    def set_pos(self, x: int or float, y: int or float) -> None:
        s = self.parent.g.display.scale
        x *= s[0]
        y *= s[1]
        return super().set_pos(x, y)

    def change_anim(self, a_id: str or None=None) -> None:
        if a_id == None: a_id = 'clicked'
        super().change_anim(a_id)


# TODO: TEXT (ELEMENT) CLASS HERE
