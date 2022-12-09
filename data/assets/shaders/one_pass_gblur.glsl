#version 300 es
        precision mediump float;
        uniform sampler2D Texture;
        uniform ivec2 size;
        in vec2 v_text;

        out vec4 f_color;

        const float TWO_PI = 6.28319f;
        const float E = 2.71828f;
        const float spread = 5.0f;

        void main() {
                vec4 color = vec4(0.0f, 0.0f, 0.0f, 0.0f);
                float sum = 0.0f;
                vec2 p_size = vec2(1.0f/float(size.x), 1.0f/float(size.y));
                int r = 4;
                for (int y = -r; y <= r; y ++) {
                        for (int x = -r; x <= r; x ++) {
                                float sig2 = spread * spread;
                                float gaus = (1.0f / sqrt(TWO_PI * sig2)) * pow(E, -((float(x) * float(x)) + (float(y) * float(y))) / (2.0f * sig2));
                                sum += gaus;
                                color += gaus * texture(Texture, v_text + vec2(p_size.x * float(x), p_size.y * float(y))).rgba;
                        }
                }
                color /= sum;
                f_color = color;
        }
