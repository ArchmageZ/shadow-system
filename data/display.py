import pygame as pg, moderngl
from data.ogl import *
from data.camera import Camera


class Renderer:
    '''Object to handle collection of game objects to be rendered for DisplayHandler objects

    :param g: the Game object to which this handler belongs
    :param surf: an optional Surface to draw collected objects on
    :param light_surf: an optional Surface to draw collected light decals on
    '''
    EMPTY_SURF = pg.Surface((0, 0))
    RENDER_RES = (640, 360)

    def __init__(self, g, surf: pg.Surface or None=None, light_surf: pg.Surface or None=None):
        self.g = g
        if surf: self.surf = surf
        else:    self.surf = pg.Surface(self.RENDER_RES, pg.SRCALPHA)
        if light_surf: self.l_surf = light_surf
        else:          self.l_surf = pg.Surface(self.RENDER_RES, pg.SRCALPHA)
        self.camera = Camera(g, self.RENDER_RES)
        self.camera.move_behavior = Camera.smooth

    def render(self):
        render_list = [(o.img, self.camera.apply_scroll(o.pos)) for o in self.g.world.render_list]

        self.surf.blits(render_list, doreturn=0)
        for l in self.g.world.light_list:
            l.draw(self.l_surf, self.camera.true_scroll)


class DisplayHandler:
    '''Object to handle both hardware and software rendering tasks for game.py

    :param g: the Game object to which this handler belongs
    :param res: the (width, height) of the output window
    :param flags: the bitwise flags for the pygame display mode, loaded from settings in game.py
    '''

    EMPTY_SURF = pg.Surface((0, 0))
    RENDER_RES = Renderer.RENDER_RES

    def __init__(self, g, res=(0, 0), flags=None):
        self.g = g
        self.surfaces = {}
        self.flags = pg.OPENGL | pg.DOUBLEBUF
        if flags: self.flags |= flags

        pg.display.set_mode(size=res, flags=self.flags)
        self.res = pg.display.get_window_size()
        self.ctx = moderngl.create_context()
        init('data/assets/shaders', self.ctx)

        self.screen = GLSurf( self.RENDER_RES, self.ctx, self.ctx.screen)
        self.screen.res = self.res
        self.surf = self.screen.surf

        # CREATE DRAWING SURFACES HERE
        color = (0.95, 0.6, 0.75)
        u_data = { 'size' : {'format': '2i', 'data': self.RENDER_RES},
                   'color': {'format': '3f', 'data': color}}
        s = self.create_ogl_surface('render'  , self.RENDER_RES)
        s.program_shader('outline', u_data)
        s = self.create_ogl_surface('lighting', self.RENDER_RES)
        s.program_shader('one_pass_gblur', u_data)

        self.surfaces['lighting'].texture.filter = moderngl.LINEAR, moderngl.LINEAR

        self.renderer = Renderer(g, self['render'].surf, self['lighting'].surf)

    def __getitem__(self, item:str) -> GLSurf:
        if item in self.surfaces:
            return self.surfaces[item]
        return self.screen

    @property
    def scale(self) -> tuple[int or float, int or float]:
        return self.RENDER_RES[0] / self.res[0], self.RENDER_RES[1] / self.res[1]

    def create_ogl_surface(self, id:str, res:tuple) -> GLSurf:
        self.surfaces.update( {id: GLSurf(res, self.ctx)} )
        return self.surfaces[id]

    def draw(self):

        self.surf.fill((60, 25, 25, 255)) # BACKGROUND RENDER

        self.renderer.render()
        img = self.get_shaded('render')
        self.surf.blit(img, (0, 0))

        img = self.get_shaded('lighting')
        self.surf.blit(img, (0, 0), special_flags=pg.BLEND_RGB_ADD)

        self.g.guis.draw(self.surf)

        self.screen.render()
        pg.display.flip()

    def get_shaded(self, surf_id: str) -> pg.Surface:
        if surf_id in self.surfaces:
            self[surf_id].render()
            return capture_render(self[surf_id].fbo, self[surf_id].res)

    def resize(self, new_res):
        if self.flags & pg.RESIZABLE:  # CHECK IF THE WINDOW WAS SET TO RESIZABLE
            self.res = new_res
            self.screen.res = new_res
