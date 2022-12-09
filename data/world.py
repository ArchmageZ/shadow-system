import os
from . import basic
from .containers import *
from .entities import *


class World:
    def __init__(self, g, path: str='data/assets/world') -> None:
        self.g = g
        self.chunks = {}
        self.entities = {}
        self.generated_ids = 0

        self.chunk_db = {}
        os.makedirs(path, exist_ok=True)
        for file in os.listdir(path):
            c_data = basic.load_json(path + '/' + file)
            c_id = file.removesuffix('.json')
            for tile in c_data:
                if 't' in tile: 
                    tile['t'] = globals().get(tile['t'], Tile)
                if 'anim' in tile: tile['anim'] = AssetHandler.get_anim(tile['anim'])
            self.chunk_db[c_id] = c_data

    def __getitem__(self, id: int) -> Entity or Light or None:
        return self.entities.get(id, None)

    def update(self, d_time: float=1.0) -> None:
        update_rect = self.g.camera.rect
        x_chunks = range(update_rect.left // CHUNKSIZE, (update_rect.right // CHUNKSIZE) + 1)
        y_chunks = range(update_rect.top // CHUNKSIZE, (update_rect.bottom // CHUNKSIZE) + 1)
        for y in y_chunks:
            for x in x_chunks:
                c = self.get_chunk(x, y)
                c.update(d_time=d_time)

    def feed(self, code: str, data: dict) -> None:
        update_rect = self.g.camera.rect
        x_chunks = range(update_rect.left // CHUNKSIZE, (update_rect.right // CHUNKSIZE) + 1)
        y_chunks = range(update_rect.top // CHUNKSIZE, (update_rect.bottom // CHUNKSIZE) + 1)
        for y in y_chunks:
            for x in x_chunks:
                c = self.get_chunk(x, y)
                c.feed(code, data)

    def spawn(self) -> None:
        update_rect = self.g.camera.rect
        x_chunks = range(update_rect.left // CHUNKSIZE, (update_rect.right // CHUNKSIZE) + 1)
        y_chunks = range(update_rect.top // CHUNKSIZE, (update_rect.bottom // CHUNKSIZE) + 1)
        for y in y_chunks:
            for x in x_chunks:
                self.get_chunk(x, y).spawn()

    @property
    def collision_list(self) -> list:
        l = []
        update_rect = self.g.camera.rect
        x_chunks = range(update_rect.left // CHUNKSIZE, (update_rect.right // CHUNKSIZE) + 1)
        y_chunks = range(update_rect.top // CHUNKSIZE, (update_rect.bottom // CHUNKSIZE) + 1)
        for y in y_chunks:
            for x in x_chunks:
                c = self.get_chunk(x, y)
                l.extend([e for e in c.entities if e.collides])
                l.extend([t for t in c.tiles if t.collides])
        return l

    @property
    def render_list(self) -> list:
        l = []
        update_rect = self.g.camera.rect
        x_chunks = range(update_rect.left // CHUNKSIZE, (update_rect.right // CHUNKSIZE) + 1)
        y_chunks = range(update_rect.top // CHUNKSIZE, (update_rect.bottom // CHUNKSIZE) + 1)
        for y in y_chunks:
            for x in x_chunks:
                c = self.get_chunk(x, y)
                l.extend(c.entities)
                l.extend(c.tiles)
        return l

    @property
    def light_list(self) -> list:
        l = []
        rect = self.g.camera.rect
        x_chunks = range(rect.left // CHUNKSIZE, (rect.right // CHUNKSIZE) + 1)
        y_chunks = range(rect.top // CHUNKSIZE, (rect.bottom // CHUNKSIZE) + 1)
        for y in y_chunks:
            for x in x_chunks:
                c = self.get_chunk(x, y)
                l.extend(c.lights)
        return l

    def load(self, chunk_id: str, x: int, y: int) -> Chunk:
        if chunk_id not in self.chunk_db:
            return self._make_empty(x, y)
        self.chunks[(x, y)] = Chunk(self.g, x, y)
        for tile in self.chunk_db[chunk_id]:
            tile = tile.copy()
            t = tile.pop('t', Tile)
            self.create_entity(t, **tile)
        return self.chunks[(x, y)]

    def get_chunk(self, x: int, y: int, chunkified: bool=True) -> Chunk:
        if not chunkified: 
            x //= CHUNKSIZE
            y //= CHUNKSIZE
        c = self.chunks.get((x, y), False)
        if not c:
            c = self._make_empty(x, y)
        return c

    def _make_empty(self, x: int, y: int) -> Chunk:
        c = self.chunks[(x, y)] = Chunk(self.g, x, y)
        return c

    def create_entity(self, t, **kwargs) -> Entity or Light:
        c = self.get_chunk(kwargs.get('x', 0), kwargs.get('y', 0), chunkified=False)

        new = t(id=self.generated_ids, g=self.g)
        for kw in kwargs:
            if hasattr(new, kw): setattr(new, kw, kwargs[kw])
        if hasattr(new, 'chunk'): setattr(new, 'chunk', c)

        self.generated_ids += 1
        self.entities.update( {new.id: new} )

        if isinstance(new, Tile): c.tiles.append(new)
        elif isinstance(new, Light): c.lights.append(new)
        else: c.entities.append(new)

        return new
