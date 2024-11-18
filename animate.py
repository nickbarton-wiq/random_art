from array import array

import pygame

import moderngl
import moderngl_window

from randomart import get_fragment_shader


class Pygame(moderngl_window.WindowConfig):
    """
    Example drawing a pygame surface with moderngl.
    """
    title = "Pygame"
    window_size = 1600, 900

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.wnd.name != 'pygame2':
            raise RuntimeError('This example only works with --window pygame2 option')

        # The resolution of the pygame surface
        self.pg_res = self.window_size
        # Create a 24bit (rgba) offscreen surface pygame can render to
        self.pg_screen = pygame.Surface(self.pg_res, flags=pygame.SRCALPHA)
        # 32 bit (rgba) moderngl texture (4 channels, RGBA)
        self.pg_texture = self.ctx.texture(self.pg_res, 4)
        # Change the texture filtering to NEAREST for pixelated look.
        self.pg_texture.filter = moderngl.NEAREST, moderngl.NEAREST
        # The pygame surface is stored in BGRA format but RGBA
        # so we simply change the order of the channels of the texture
        self.pg_texture.swizzle = 'BGRA'

        self.texture_program = self.ctx.program(
            vertex_shader="""
                #version 330
                // Vertex shader runs once for each vertex in the geometry

                in vec2 in_vert;
                in vec2 in_texcoord;
                out vec2 fragTexCoord;

                void main() {
                    // Send the texture coordinates to the fragment shader
                    fragTexCoord = in_texcoord;
                    // Resolve the vertex position
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
            """,
            fragment_shader="""
                #version 330
                uniform float time;
                in vec2 fragTexCoord;
                out vec4 finalColor;

                vec4 map_color(vec3 rgb) {
                    return vec4((rgb + 1)/2.0, 1.0);
                }

                void main() {
                    float x = fragTexCoord.x*2.0 - 1.0;
                    float y = fragTexCoord.y*2.0 - 1.0;
                    float t = sin(time);
                    finalColor = map_color(""" + get_fragment_shader() + """);
                }
            """,
        )

        buffer = self.ctx.buffer(
            data=array('f', [
                # Position (x, y) , Texture coordinates (x, y)
                -1.0, 1.0, 0.0, 1.0,  # upper left
                -1.0, -1.0, 0.0, 0.0,  # lower left
                1.0, 1.0, 1.0, 1.0,  # upper right
                1.0, -1.0, 1.0, 0.0,  # lower right
            ])
        )
        self.quad_fs = self.ctx.vertex_array(
            self.texture_program,
            [
                (
                    # The buffer containing the data
                    buffer,
                    # Format of the two attributes. 2 floats for position, 2 floats for texture coordinates
                    "2f 2f",
                    # Names of the attributes in the shader program
                    "in_vert", "in_texcoord",
                )
            ],
        )

    def render(self, time: float, frame_time: float):
        """Called every frame"""
        self.render_pygame(time)
        self.texture_program['time'] = time
        # Enable blending for transparency
        self.ctx.enable(moderngl.BLEND)
        # Bind the texture to texture channel 0
        self.pg_texture.use(location=0)
        # Render the quad to the screen. Will use the texture we bound above.
        self.quad_fs.render(mode=moderngl.TRIANGLE_STRIP)
        # Disable blending
        self.ctx.disable(moderngl.BLEND)

    def render_pygame(self, time: float):
        """Render to offscreen surface and copy result into moderngl texture"""
        self.pg_screen.fill((0, 0, 0, 0))  # Make sure we clear with alpha 0!
        # Get the buffer view of the Surface's pixels
        # and write this data into the texture
        texture_data = self.pg_screen.get_view('1')
        self.pg_texture.write(texture_data)


if __name__ == '__main__':
    moderngl_window.run_window_config(Pygame, args=('--window', 'pygame2'))  # type: ignore
