import pygame as pg, os
from . import animation, basic


class AssetHandler:
    EMPTY_COLLECTION = animation.AnimationCollection('empty', {})
    EMPTY_SURF = pg.Surface((0, 0))
    EMPTY_MASK = pg.mask.Mask((0, 0))
    palettes = {}
    selected_palette = ''
    anim_dict = {}
    font_dict = {}
    shaders = {}

    @staticmethod
    def get_drawn(col_id: str, anim_id:str, img_index=0, dir_id=0):
        if not 0 <= dir_id <= 1: dir_id = 0
        if col_id in AssetHandler.anim_dict and anim_id in AssetHandler.anim_dict[col_id]:
            if 0 <= img_index < len(AssetHandler.anim_dict[col_id][anim_id][0]):
                return AssetHandler.anim_dict[col_id][anim_id][1][dir_id][img_index]
        return AssetHandler.EMPTY_SURF

    @staticmethod
    def get_mask(col_id: str, anim_id: str, img_index= 0, dir_id=0):
        if not 0 <= dir_id <= 1: dir_id = 0
        if col_id in AssetHandler.anim_dict and anim_id in AssetHandler.anim_dict[col_id]:
            if 0 <= img_index < len(AssetHandler.anim_dict[col_id][anim_id][0]):
                return AssetHandler.anim_dict[col_id][anim_id][2][dir_id][img_index]
        return AssetHandler.EMPTY_MASK

    @staticmethod
    def init():
        AssetHandler.init_palettes('data/assets/palettes.json')
        AssetHandler.init_anim('data/assets/anim')
        AssetHandler.init_font('data/assets/font')
        AssetHandler.init_shaders('data/assets/shaders')

    @staticmethod
    def init_palettes(path: str):
        AssetHandler.palettes = {}

    @staticmethod
    def init_anim(path: str):
        AssetHandler.anim_dict = {}
        os.makedirs(path, exist_ok=True)

        def load_anim(path):
            a_id = path.split('/')[-1]
            a_dict = {}
            cfg = {}
            for line in basic.load_file(path + '/anim.cfg').split('\n'):
                line = line.split(' ')
                if len(line) < 3:
                    line.append('')
                n, times, tags = line
                cfg.update( {n: (times, tags)} )
            anims = os.listdir(path)
            anims.remove('anim.cfg')
            for anim in anims:
                anim_imgs, anim_masks = basic.load_sprite_sheet(path + '/' + anim)
                anim = anim.split('.')[0]
                anim_frames = [5 for i in range(len(anim_imgs[0]))]
                anim_tags = {}
                if anim in cfg:
                    anim_frames = [int(t) for t in cfg[anim][0].split(';')]
                    for tag in cfg[anim][1].split(';'):
                        if len(tag) > 0:
                            t_id, t_v = tag.split(':')
                            anim_tags.update( {t_id: t_v} )
                a_dict.update( {anim: (tuple(anim_frames), anim_imgs, anim_masks, anim_tags)} )
            AssetHandler.anim_dict.update( {a_id: a_dict} )

        def probe_path(path):
            if 'anim.cfg' in os.listdir(path):
                load_anim(path)
                return
            for dir in os.listdir(path):
                if dir.count('.') == 0:
                    probe_path(path + '/' + dir)

        probe_path(path)

    @staticmethod
    def init_font(path: str):
        pass

    @staticmethod
    def init_shaders(path: str):
        AssetHandler.shaders = {}
        os.makedirs(path, exist_ok=True)

        for shader in os.listdir(path):
            shader_literal = basic.load_file(path + '/' + shader)
            shader_id = shader.split('.')[0]
            AssetHandler.shaders.update( {shader_id: shader_literal} )

    @staticmethod
    def change_palette(p_id: str):
        if p_id in AssetHandler.palettes and AssetHandler.selected_palette != p_id:
            old_p = AssetHandler.palettes[AssetHandler.selected_palette]
            new_p = AssetHandler.palettes[p_id]
            for col_id in AssetHandler.anim_dict:
                for anim_id in AssetHandler.anim_dict[col_id]:
                    for img in AssetHandler.anim_dict[col_id][anim_id][1][0]:
                        basic.swap_palette(img, old_p, new_p)
                    for img_f in AssetHandler.anim_dict[col_id][anim_id][1][1]:
                        basic.swap_palette(img_f, old_p, new_p)
            AssetHandler.selected_palette = p_id

    @staticmethod
    def get_anim(a_id: str):
        if a_id in AssetHandler.anim_dict:
            r = animation.AnimationCollection(a_id, AssetHandler.anim_dict[a_id])
            return r
        return AssetHandler.EMPTY_COLLECTION

    @staticmethod
    def get_font(f_id: str):
        pass

    @staticmethod
    def get_shader(s_id: str):
        if s_id in AssetHandler.shaders:
            return AssetHandler.shaders[s_id]
        return AssetHandler.shaders['def_fragment']
