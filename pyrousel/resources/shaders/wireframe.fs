#version 330

in vec4 wireColor;
out vec4 f_color;

void main() 
{
    f_color = wireColor;
}