from wgpu_shadertoy import Shadertoy
from randomart import get_fragment_shader

shader_code = """
    fn shader_main(fragCoord: vec2<f32>) -> vec4<f32> {
    let uv: vec2<f32> = fragCoord.xy / i_resolution.xy;
    let x: f32 = uv.x * 2.0 - 1.0;
    let y: f32 = uv.y * 2.0 - 1.0;
    let t: f32 = sin(i_time);
    let col: vec3<f32> = """ + get_fragment_shader() + """;
    return vec4<f32>(col, 1.0);
    }
"""

shader = Shadertoy(shader_code, resolution=(1600, 900))

if __name__ == "__main__":
    shader.show()
