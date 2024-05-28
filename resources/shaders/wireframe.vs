#version 330

layout (location = 0) in vec3 in_position;

uniform mat4 modelTransform;
uniform mat4 viewTransform;
uniform mat4 perspectiveTransform;
uniform vec4 color;

out vec4 wireColor;

void main() 
{
    mat4 mvp = perspectiveTransform * viewTransform * modelTransform;
    wireColor = color;
    gl_Position = mvp * vec4(in_position, 1.0);
}