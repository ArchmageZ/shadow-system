import struct, moderngl, os
import pygame as pg
from . import basic


global shaders
shaders = {}


def init(path: str, ctx: moderngl.Context):
    """Initialize and load shaders from path
    :param path: The path to the shaders folder, in str format
    """
    global shaders
    DEF_CTX = ctx
    DEF_CTX.enable_only(DEF_CTX.BLEND)
    DEF_CTX.blend_func = (
        moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA,
        moderngl.ONE, moderngl.ONE
    )

    TEXTURE_COORDS = [0, 1, 1, 1, 0, 0, 1, 0]
    WORLD_COORDS = [-1, -1, 1, -1, -1, 1, 1, 1]
    RENDER_INDICES = [0, 1, 2, 1, 2, 3]

    shaders = {}
    vertex_shader = """
    #version 300 es
        in vec2 vert;
        in vec2 in_text;

        out vec2 v_text;
        void main() {
            gl_Position = vec4(vert, 0.0, 1.0);
            v_text = in_text;
        }
    """

    vbo = DEF_CTX.buffer(struct.pack('8f', *WORLD_COORDS))
    uvmap = DEF_CTX.buffer(struct.pack('8f', *TEXTURE_COORDS))
    ibo = DEF_CTX.buffer(struct.pack('6I', *RENDER_INDICES))
    vao_content = [
        (vbo, '2f', 'vert'),
        (uvmap, '2f', 'in_text'),
    ]

    os.makedirs(path, exist_ok=True)
    for file in os.listdir(path):
        fragment_shader = basic.load_file(path + '/' + file)
        prog = DEF_CTX.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)

        vao =  DEF_CTX.vertex_array(prog, vao_content, index_buffer=ibo)
        shaders.update( {file.split('.')[0]: vao} )


def capture_render(fb: moderngl.Framebuffer, viewport=(640, 360)) -> pg.Surface:
    """Return the Pygame.Surface of the given ModernGL.Framebuffer"""
    w, h = fb.size
    data = fb.read(components=4)
    img = pg.image.frombuffer(data, (w, h), 'RGBA')
    return pg.transform.flip(img, flip_x=False, flip_y=True)


class GLSurf(object):
    '''Wrapper around ModernGL's render functions, using a default headless context if no context is supplied

    :param res: The (height, width) of the surface to create, in pixels
    :param ctx: The ctx for ModernGL to use for rendering, defaulting to a headless context
    :param frag_shader: The shader to load during initialization, defaulting to a passthrough shader
    :param uniform_data: Uniform data to be passed to the shader,
                format of { u_name : {format: str, data: iterable} }, defaulting to empty
    '''

    DEF_RES = (640, 360)
    CLEAR_COLOR = (0, 0, 0, 0)

    def __init__(self, res:tuple, ctx: moderngl.Context, fbo: moderngl.Framebuffer or None=None):
        if not (len(res) == 2 and isinstance(res[0], int) and isinstance(res[1], int)):
            res = self.DEF_RES
        self.res = res
        self.ctx = ctx
        if fbo:
            self.fbo = fbo
        else:
            self.fbo = self.ctx.simple_framebuffer(res)

        self.surf = pg.Surface(self.res, flags=pg.SRCALPHA).convert_alpha()
        self.surf.fill(self.CLEAR_COLOR)
        self.texture = t = self.ctx.texture(self.surf.get_size(), 4)
        t.repeat_x, t.repeat_y = False, False
        t.filter = moderngl.NEAREST, moderngl.NEAREST
        t.swizzle = 'RGBA'

        self.program_shader()

    def render(self):
        self.fbo.use()
        self.fbo.clear( *[c/255 for c in self.CLEAR_COLOR] )
        self.fbo.viewport = (0, 0) + self.res

        self.texture.write(self.surf.get_view('1'))
        self.texture.use()

        self.vao.render()
        self.surf.fill(self.CLEAR_COLOR, special_flags=pg.BLEND_RGBA_MIN)

    def program_shader(self, frag_shader='def_fragment', uniform_config={}):
        global shaders
        if frag_shader not in shaders:
            frag_shader = 'def_fragment'
        self.vao = shaders[frag_shader]
        self.shader = frag_shader
        prog = self.vao.program

        for u_data in uniform_config:
            u = prog.get(u_data, None)
            if u:
                u_data = uniform_config[u_data]
                u.write( struct.pack(u_data['format'], *u_data['data']) )