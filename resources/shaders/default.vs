#version 330

layout (location = 0) in vec3 in_position;
layout (location = 1) in vec3 in_normal;
layout (location = 2) in vec2 in_texcoord;

out vec3 vertexNormal;
out vec3 objectNormal;
out vec2 texcoord;

uniform mat4 modelTransform;
uniform mat4 viewTransform;
uniform mat4 perspectiveTransform;

void main() 
{
    mat4 mvp = perspectiveTransform * viewTransform * modelTransform;
    vertexNormal = normalize(in_normal);
    objectNormal = (modelTransform * vec4(vertexNormal.xyz, 0.0)).xyz;
    texcoord = in_texcoord;
    gl_Position = mvp * vec4(in_position, 1.0);
}