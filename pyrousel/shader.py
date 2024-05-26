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

                out vec3 vnormal;

                uniform mat4 modelTransform;
                uniform mat4 viewTransform;
                uniform mat4 perspectiveTransform;

                void main() {
                    mat4 mvp = perspectiveTransform * viewTransform * modelTransform;
                    vnormal = (mvp * vec4(in_normal, 1.0)).xyz;
                    gl_Position = mvp * vec4(in_position, 1.0);
                }
            '''

        self.fragment_source: str = '''
                #version 330

                in vec3 vnormal;

                out vec4 f_color;

                void main() {
                    vec3 sun = vec3(1, 0.0, 1);
                    float ndotl = dot(normalize(sun), normalize(vnormal));

                    vec3 basecol = vec3(0.9, 0.5, 0.1);
                    vec3 ambience = basecol * 0.05;
                    vec3 diff = clamp(ndotl * vec3(1,1,1), 0.0, 1.0);
                    vec3 final = clamp(ambience + diff, 0.0, 1.0);

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
                uniform vec3 color;

                out vec3 wireColor;

                void main() {
                    mat4 mvp = perspectiveTransform * viewTransform * modelTransform;
                    wireColor = color;
                    gl_Position = mvp * vec4(in_position, 1.0);
                }
            '''

        self.fragment_source: str = '''
                #version 330

                in vec3 wireColor;
                out vec4 f_color;

                void main() {
                    f_color = vec4(wireColor, 1.0);
                }
            '''