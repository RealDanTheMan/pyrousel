class ShaderBase(object):
    def __init__(self):
        self.vertex_source = None
        self.fragment_source = None

class ShaderFallback(ShaderBase):
    def __init__(self):
        super().__init__()
        self.vertex_source: str = '''
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

                void main() {
                    mat4 mvp = perspectiveTransform * viewTransform * modelTransform;
                    vertexNormal = normalize(in_normal);
                    objectNormal = (modelTransform * vec4(vertexNormal.xyz, 0.0)).xyz;
                    texcoord = in_texcoord;
                    gl_Position = mvp * vec4(in_position, 1.0);
                }
            '''

        self.fragment_source: str = '''
                #version 330

                uniform mat4 modelTransform;
                uniform float visualise_normals;
                uniform float visualise_texcoords;

                in vec3 vertexNormal;
                in vec3 objectNormal;
                in vec2 texcoord;

                out vec4 f_color;

                void main() {
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
            '''

class ShaderWireframeFallback(ShaderBase):
    def __init__(self):
        super().__init__()
        self.vertex_source: str = '''
                #version 330

                layout (location = 0) in vec3 in_position;

                uniform mat4 modelTransform;
                uniform mat4 viewTransform;
                uniform mat4 perspectiveTransform;
                uniform vec4 color;

                out vec4 wireColor;

                void main() {
                    mat4 mvp = perspectiveTransform * viewTransform * modelTransform;
                    wireColor = color;
                    gl_Position = mvp * vec4(in_position, 1.0);
                }
            '''

        self.fragment_source: str = '''
                #version 330

                in vec4 wireColor;
                out vec4 f_color;

                void main() {
                    f_color = wireColor;
                }
            '''