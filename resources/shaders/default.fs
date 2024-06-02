#version 330

in vec3 vertex_position;
in vec3 vertex_normal;
in vec3 object_normal;
in vec2 texcoord;
in vec3 color;

out vec4 f_color;

uniform mat4 view_transform;
uniform vec3 light_color;
uniform vec3 light_position;
uniform float visualise_normals;
uniform float visualise_texcoords;
uniform float visualise_colors;

float LambertCoefficient(vec3 normal, vec3 light_dir)
{
    float NdotL = max(0.0, dot(normal, light_dir));
    return pow(NdotL * 0.5 + 0.5, 2.0);
}

float PhongCoefficient(vec3 view_dir, vec3 light_dir, vec3 normal)
{
    vec3 view_light = normalize(view_dir + light_dir);
    float angle = max(dot(view_light, normal), 0.0);
    return pow(angle, 1.0);
}

void main() 
{
    // Temporary sunlight
    vec3 sun = vec3(1, 0.0, 1);
    
    // Lighting inputs
    vec3 camera_position = view_transform[3].xyz;
    vec3 surface_normal = normalize(object_normal);
    vec3 view_dir = normalize(camera_position - vertex_position);
    vec3 light_dir = normalize(light_position - vertex_position);
    vec3 base_color = vec3(0.9, 0.5, 0.1);
    vec3 ambient_color = base_color * 0.05;

    // Lighting components
    vec3 diffuse = LambertCoefficient(surface_normal, light_dir) * base_color * light_color;
    vec3 spec = PhongCoefficient(view_dir, light_dir, surface_normal) * light_color;
    vec3 final = diffuse + spec;
    
    // Debug visualisation
    vec3 debugNormals = (vertex_normal + vec3(1,1,1) * 0.5);
    vec3 debugTexcoords = vec3(texcoord.xy, 0.0);
    vec3 debugColors = color;
    final = mix(final, debugNormals, visualise_normals);
    final = mix(final, debugTexcoords, visualise_texcoords);
    final = mix(final, debugColors, visualise_colors);

    // Final pixel color output
    f_color = vec4(final, 1.0);
}