#version 330

layout (location = 0) in vec3 in_position;

uniform mat4 model_transform;
uniform mat4 view_transform;
uniform mat4 perspective_transform;
uniform vec4 color;

out vec4 wireColor;

void main() 
{
    mat4 mvp = perspective_transform * view_transform * model_transform;
    wireColor = color;
    gl_Position = mvp * vec4(in_position, 1.0);
}