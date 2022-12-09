import pygame as pg, json, os, configparser


SPRITE_COLORKEY = pg.Color(255, 255, 255)


def _oserr(path) -> None:
    err_path = path.split('/')[:-1]
    err_path = "/".join(err_path)
    os.makedirs(err_path, exist_ok=True)
    if len(os.listdir(err_path)) > 0:
        print('ERR: \tfile does not exist at the specified path')
    else:
        print('ERR: \tthe path was incorrectly configured and has been created for debugging')


def load_file(path: str) -> str:
    r = ""

    try:
        f = open(path)
        r = f.read()
        f.close()
    except OSError:
        print('ERR: failed to load file at \t' + path)
        _oserr(path)

    return r


def load_json(path: str) -> dict:
    r = {}

    try:
        r = json.loads(load_file(path))
    except json.decoder.JSONDecodeError:
        print('ERR: json file incorrectly formated at \t' + path)

    return r


def load_ini(path: str) -> configparser.ConfigParser:
    r = configparser.ConfigParser()

    try:
        r.read_string(load_file(path))
    except configparser.Error:
        print('ERR: ini file incorrectly formated at \t' + path)

    return r


def save_file(path: str, content: str) -> None:
    try:
        f = open(path, mode='w')
        f.write(content)
        f.close()
    except OSError:
        print('ERR: failed to write file at \t' + path)
        _oserr(path)


def save_json(path: str, content: dict) -> None:
    content = json.dumps(content, indent=4, separators=(',',': '))
    save_file(path, content)


def save_ini(path: str, content: configparser.ConfigParser) -> None:
    save_file(path, "")
    with open(path, mode='w') as file:
        content = content.write(file)
        file.close()


def swap_palette(img, old_p, new_p) -> None:
    img_arr = pg.PixelArray(img)
    for i in range(len(old_p)) if len(old_p) <= len(new_p) else range(len(new_p)):
        img_arr.replace(old_p[i], new_p[i])
    img = img_arr.make_surface()


def swap_color(img, old_c, new_c) -> None:
    img_arr = pg.PixelArray(img)
    img_arr.replace(old_c, new_c)
    img = img_arr.make_surface()


def load_sprite_sheet(path) -> tuple[tuple[tuple[pg.Surface, ...], tuple[pg.Surface, ...]],
                               tuple[tuple[pg.mask.Mask, ...], tuple[pg.mask.Mask, ...]]]:
    ss_img = pg.image.load(path)
    imgs, imgs_f = (), ()
    left_x, bottom_y = 0, 0
    img_widths = []
    for x in range(ss_img.get_width() + 1):
        if x == ss_img.get_width() or ss_img.get_at((x, 0))[3] == 0:
            img_widths.append(x - left_x)
            left_x = x + 1
    left_x = 0
    for width in img_widths:
        for y in range(ss_img.get_height() + 1):
            if y == ss_img.get_height() or ss_img.get_at((left_x, y))[3] == 0:
                break;

        img = ss_img.subsurface( pg.Rect(left_x, 0, width, y) ).copy().convert()
        img.set_colorkey(SPRITE_COLORKEY)
        img_f = pg.transform.flip(img, flip_x=True, flip_y=False)
        img_f.set_colorkey(SPRITE_COLORKEY)

        imgs += (img,)
        imgs_f += (img_f,)
        left_x += width + 1
    masks = ()
    masks_f = ()
    for img in imgs:
        mask = pg.mask.from_surface(img)
        masks += (mask,)
    for img_f in imgs_f:
        mask_f = pg.mask.from_surface(img_f)
        masks_f += (mask_f,)

    return (imgs, imgs_f), (masks, masks_f)
