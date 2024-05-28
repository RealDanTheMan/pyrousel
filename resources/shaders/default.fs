#version 330

uniform mat4 modelTransform;
uniform float visualise_normals;
uniform float visualise_texcoords;

in vec3 vertexNormal;
in vec3 objectNormal;
in vec2 texcoord;

out vec4 f_color;

void main() 
{
    vec3 sun = vec3(1, 0.0, 1);
    float ndotl = dot(normalize(sun), normalize(objectNormal));

    vec3 basecol = vec3(0.9, 0.5, 0.1);
    vec3 ambience = basecol * 0.05;
    vec3 diff = clamp(ndotl * vec3(1,1,1), 0.0, 1.0);
    vec3 debugNormals = (vertexNormal + vec3(1,1,1) * 0.5);
    vec3 debugTexcoords = vec3(texcoord.xy, 0.0);
    vec3 final = clamp(ambience + diff, 0.0, 1.0);
    
    final = mix(final, debugNormals, visualise_normals);
    final = mix(final, debugTexcoords, visualise_texcoords);

    f_color = vec4(final, 1.0);
}