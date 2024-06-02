import numpy as np
from pyrr import Matrix44, Vector3
from pyrousel.transform import Transform
from pyrousel.trimesh import trimesh as trimesh

class Model(object):
    def __init__(self):
        self.vertices: List(np.array) = np.array([], dtype='f4')
        self.normals: List(np.array) = np.array([], dtype='f4')
        self.indices: List(np.array) = np.array([], dtype='i4')
        self.texcoords: List(np.array) = np.array([], dtype='f4')
        self.colors: List(np.array) = np.array([], dtype='f4')
        self.transform: Transform = Transform()
        self.minext: Vector3 = Vector3([0.0, 0.0, 0.0])
        self.maxext: Vector3 = Vector3([0.0, 0.0, 0.0])

    def __repr__(self):
        num_vertices = int(len(self.vertices) / 3)
        num_indices = int(len(self.indices) / 3)
        num_normals = int(len(self.normals) / 3)
        num_texcoords = int(len(self.texcoords) / 3)
        num_colors = int(len(self.colors) / 3)

        return f'Model -> vertices:{num_vertices} normals:{num_normals} texcoords:{num_texcoords} colors:{num_colors} indices:{num_indices}'

    def RecomputeBounds(self):
        """Recalucaltes local extends/bounds based on the vertex data"""
        for i in range(0, len(self.vertices), 3):
            self.minext.x = min(self.minext.x, self.vertices[i])
            self.minext.y = min(self.minext.y, self.vertices[i+1])
            self.minext.z = min(self.minext.z, self.vertices[i+2])
            self.maxext.x = max(self.maxext.x, self.vertices[i])
            self.maxext.y = max(self.maxext.y, self.vertices[i+1])
            self.maxext.z = max(self.maxext.z, self.vertices[i+2])

class RenderModel(Model):
    def __init__(self):
        super().__init__()
        self.shader = None
        self.vertex_buffer = None
        self.normal_buffer = None
        self.texcoord_buffer = None
        self.color_buffer = None
        self.index_buffer = None
        self.vertex_array = None

class PrimitiveFactory:
    @staticmethod
    def CreateTriangle(size: float = 1.0) -> RenderModel:
        """Creates and returns single equilateral triangle primitive model"""
        model = RenderModel()

        pos = size * 0.5
        height = size * 0.433
        model.vertices = np.array([
            0.0, height, 0.0,
            pos, -height, 0.0,
            -pos, -height, 0.0,
        ], dtype='f4')

        model.normals = np.array([
            0.0, 0.0, 1.0,
            0.0, 0.0, 1.0,
            0.0, 0.0, 1.0
        ])

        model.indices = np.array([
            0, 1, 2
        ], dtype='i4')

        return model

    @staticmethod
    def CreateRectangle(size: float = 1.0) -> RenderModel:
        """Creates and returns single rectangle primitive model"""
        model = RenderModel()

        pos = size * 0.5
        model.vertices = np.array([
            -pos, pos, 0.0,
            pos, pos, 0.0,
            pos, -pos, 0.0,
            -pos, -pos, 0.0,
        ], dtype='f4')

        model.normals = np.array([
            0.0, 0.0, 1.0,
            0.0, 0.0, 1.0,
            0.0, 0.0, 1.0,
            0.0, 0.0, 1.0,
        ])

        model.indices = np.array([
            0, 1, 2,
            0, 2, 3
        ], dtype='i4')

        return model

    def CreateBox(size: float = 1.0) -> RenderModel:
        """Creates and returns single box primitive model"""
        model = RenderModel()

        hsize = size * 0.5
        model.vertices = np.array([
            # Top plane
            -hsize, hsize, -hsize,
            hsize, hsize, -hsize,
            hsize, hsize, hsize,
            -hsize, hsize, hsize,
            # Bottom plane
            -hsize, -hsize, -hsize,
            hsize, -hsize, -hsize,
            hsize, -hsize, hsize,
            -hsize, -hsize, hsize,
        ], dtype='f4')

        ang = 0.57735
        model.normals = np.array([
            # Top plane
            -ang, ang, -ang,
            ang, ang, -ang,
            ang, ang, ang,
            -ang, ang, ang,
            # Bottom plane
            -ang, -ang, -ang,
            ang, -ang, -ang,
            ang, -ang, ang,
            -ang, -ang, ang,
        ], dtype='f4')

        model.indices = np.array([
            # Top plane
            0, 1, 2,
            0, 2, 3,
            # Front plane
            2, 7, 3,
            2, 6, 7,
            # Bottom plane
            7, 5, 4,
            7, 6, 5,
            # Back plane
            5, 4, 0,
            5, 0, 1,
            # Left Plane
            0, 7, 4,
            0, 3, 7,
            # Right plane
            2, 5, 6,
            2, 1, 5
        ], dtype='i4')

        return model

class ModelLoader():
    @staticmethod
    def LoadFromOBJ(filepath: str) -> RenderModel:
        """
        Loads model from given OBJ file

        Passed shader source should have vertex_shader and fragment_shader defined at minimum.

        At the moment only vertices and vertex normal mesh data ise supported

        Parameters
        ----------
        filepath : str
            Filepath to the OBJ file containing the model data

        Returns
        -------
        RenderModel object representing OBJ model
        """
        vertices = []
        normals = []
        texcoords = []
        indices = []
        with open(filepath, 'r') as file:
            for line in file:
                if line.startswith('v '):
                    data = list(map(float, line.strip().split()[1:]))
                    if(len(data) != 3):
                        raise Exception("Vertex format is invalid!")
                    vertices.append(data[0])
                    vertices.append(data[1])
                    vertices.append(data[2])
                elif line.startswith('vn '):
                    data = list(map(float, line.strip().split()[1:]))
                    if(len(data) != 3):
                        raise Exception("Vertex normal format is invalid!")
                    normals.append(data[0])
                    normals.append(data[1])
                    normals.append(data[2])
                elif line.startswith('vt '):
                    data = list(map(float, line.strip().split()[1:]))
                    if(len(data) < 2):
                        raise Exception("Texcoord format is invalid!")
                    texcoords.append(data[0])
                    texcoords.append(data[1])
                elif line.startswith('f '):
                    facedata = line.strip().split()[1:]
                    if(len(facedata) != 3):
                        raise Exception("Face index format is invalid!")
                    for faceset in facedata:
                        face_indices = faceset.split('/')
                        indices.append(int(face_indices[0]) - 1)
        model = RenderModel()
        model.vertices = np.array(vertices, dtype='f4')
        model.normals = np.array(normals, dtype='f4')
        model.texcoords = np.array(texcoords, dtype='f4')
        model.indices = np.array(indices, dtype='i4')
        return model
    
    @staticmethod
    def LoadModel(filepath: str) -> RenderModel:
        """
        Loads model from wide variety of formats via Trimesh library

        See https://trimesh.org/ for list of supported formats

        Parameters
        ----------
        filepath : str
            Filepath to the OBJ file containing the model data

        Returns
        -------
        RenderModel object representing OBJ model
        """
        vertices = []
        normals = []
        texcoords = []
        colors = []
        indices = []

        mesh = trimesh.load(filepath, force='mesh', process=False)
        vertices = mesh.vertices.flatten()
        indices = mesh.faces.flatten()
        normals = mesh.vertex_normals.flatten()

        # Note: Vertex color support in Trimesh is limited when meshes contain texture coords or materials
        # Will have to make modification to enable better support

        if hasattr(mesh.visual, 'uv') and mesh.visual.uv is not None:
            texcoords = mesh.visual.uv.flatten()

        if hasattr(mesh.visual, 'vertex_colors') and mesh.visual.vertex_colors is not None:
            print('Fetching pure vertex color')
            for color in mesh.visual.vertex_colors:
                colors.append(color[0] / 255)
                colors.append(color[1] / 255)
                colors.append(color[2] / 255)
        elif hasattr(mesh.visual, 'vertex_attributes') and 'color' in mesh.visual.vertex_attributes:
            print('Fetching vertex color via vertex attributes')
            for color in mesh.visual.vertex_attributes["color"]:
                colors.append(color[0] / 255)
                colors.append(color[1] / 255)
                colors.append(color[2] / 255)

        model = RenderModel()
        model.vertices = np.array(vertices, dtype='f4')
        model.normals = np.array(normals, dtype='f4')
        model.texcoords = np.array(texcoords, dtype='f4')
        model.colors = np.array(colors, dtype='f4')
        model.indices = np.array(indices, dtype='i4')
        return model