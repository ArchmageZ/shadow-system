#version 300 es
        precision mediump float;
        uniform sampler2D Texture;
        uniform ivec2 size;
        uniform vec3 color;
        in vec2 v_text;

        out vec4 f_color;
        void main() {
                vec2 offset = vec2(1.0f / float(size.x), 1.0f / float(size.y));
                vec4 col = texture(Texture, v_text).rgba;
                if (col.a > 0.5)
                        f_color = col;
                else {
                        float a = texture(Texture, vec2(v_text.x + offset.x, v_text.y)).a +
                            texture(Texture, vec2(v_text.x, v_text.y - offset.y)).a +
                            texture(Texture, vec2(v_text.x - offset.x, v_text.y)).a +
                            texture(Texture, vec2(v_text.x, v_text.y + offset.y)).a;
                        if (col.a < 1.0 && a > 0.0)
                            f_color = vec4(color, 1.0f);
                        else
                            f_color = col;
                }
        }