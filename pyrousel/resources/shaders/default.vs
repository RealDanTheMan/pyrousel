#version 330

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec2 in_texcoord;
layout (location = 3) in vec3 in_color;

out vec3 vertex_position;
out vec3 vertex_normal;
out vec3 object_normal;
out vec2 texcoord;
out vec3 color;
out vec3 camera_position;

uniform mat4 model_transform;
uniform mat4 view_transform;
uniform mat4 perspective_transform;

void main() 
{
    mat4 mvp = perspective_transform * view_transform * model_transform;
    vertex_position = (model_transform * vec4(in_position, 1.0)).xyz;
    vertex_normal = normalize(in_normal);
    object_normal = (model_transform * vec4(vertex_normal.xyz, 0.0)).xyz;
    texcoord = in_texcoord;
    color = in_color;
    gl_Position = mvp * vec4(in_position, 1.0);
}