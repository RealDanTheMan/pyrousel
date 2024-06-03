#version 330

#define PI 3.1415926535897932384626433832795

in vec3 vertex_position;
in vec3 vertex_normal;
in vec3 object_normal;
in vec2 texcoord;
in vec3 color;

out vec4 f_color;

uniform mat4 view_transform;
uniform vec3 light_color;
uniform vec3 light_position;
uniform vec3 mat_base_color;
uniform float mat_roughness;
uniform float mat_spec_intensity;
uniform float visualise_normals;
uniform float visualise_texcoords;
uniform float visualise_colors;

float ComputeDiffuse(float NdotL)
{
    return pow(NdotL * 0.5 + 0.5, 2.0);
}

vec3 ComputeFresnel(float NdotH, vec3 F0)
{
    return F0 + (1.0 - F0) * pow(1.0 - NdotH, 5.0);
}

float ComputeGGX(float theta, float roughness)
{
    float r = pow(roughness, 4);
    float thetasq = theta * theta;
    float ggx = 1.0 / (theta + sqrt(r + thetasq - r * thetasq));
    
    return ggx;
}

float ComputeSpecularBRDF(
    float NdotL,
    float NdotV,
    float NdotH,
    float roughness,
    float intensity,
    vec3 F0
)
{
    vec3 fresnel = ComputeFresnel(NdotH, F0);
    float ggx = ComputeGGX(NdotL, roughness) * ComputeGGX(NdotV, roughness);
    float spec = (1.0 / PI) * fresnel.x * ggx * intensity;
    
    return spec;
}

void main() 
{
    // Lighting inputs
    vec3 camera_position = view_transform[3].xyz;
    vec3 surface_normal = normalize(object_normal);
    vec3 view_dir = normalize(vertex_position - camera_position);
    vec3 light_dir = normalize(light_position - vertex_position);
    vec3 base_color = mat_base_color;

    // BRDF inputs
    vec3 H = normalize(view_dir + light_dir); // Halfway vector between view and light
    vec3 F0 = vec3(0.04);
    float NdotH = max(0.001, dot(surface_normal, H));
    float NdotV = max(0.001, dot(surface_normal, view_dir));
    float NdotL = max(0.001, dot(surface_normal, light_dir));
    float HdotL = max(0.001, dot(H, light_dir));
    float metalness = 0.0;

    // Lighting components
    vec3 diffuse = ComputeDiffuse(NdotL) * base_color;
    vec3 spec = ComputeSpecularBRDF(NdotL, NdotV, NdotH, mat_roughness, mat_spec_intensity, F0) * vec3(1);
    vec3 final = (diffuse + spec) * light_color;
    
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