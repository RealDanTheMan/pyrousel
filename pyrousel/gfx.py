import os
from enum import Enum
import numpy as np
from dataclasses import dataclass
from pyrr import Matrix44, Vector3, Vector4
import moderngl as mgl
from pyrousel.shader import ShaderSource
from pyrousel.model import RenderModel

class WireframeMode(Enum):
    WireframeOff = 0
    WireframeOnly = 1
    WireframeShaded = 2

class VisualiserMode(Enum):
    ShowDefault = 0
    ShowNormals = 1
    ShowTexcoords = 2
    ShowColor = 3

@dataclass
class RenderHints:
    visualiser_mode = VisualiserMode.ShowDefault
    wireframe_mode = WireframeMode.WireframeShaded
    wireframe_color = Vector4([0.0, 1.0, 0.0, 1.0])

class GFX(object):
    def __init__(self, ctx: mgl.Context):
        self.__ctx = ctx
        self.__ctx.enable(mgl.DEPTH_TEST)
        self.__ctx.enable(mgl.BLEND)
        self.__ctx.blend_func = (mgl.SRC_ALPHA, mgl.ONE_MINUS_SRC_ALPHA)
        self.view_matrix: Matrix44 = Matrix44.identity().astype('float32')
        self.perspective_matrix: Matrix44  = Matrix44.identity().astype('float32')

        self.light_value = Vector3([1,1,1])

        def_shader_src = ShaderSource.LoadFromFile(
            os.path.join(os.getcwd(), 'resources/shaders/default.vs'), 
            os.path.join(os.getcwd(), 'resources/shaders/default.fs')
        )

        def_wireshader_src = ShaderSource.LoadFromFile(
            os.path.join(os.getcwd(), 'resources/shaders/wireframe.vs'), 
            os.path.join(os.getcwd(), 'resources/shaders/wireframe.fs')
        )

        self.def_shader = self.CompileShaderProgram(def_shader_src)
        self.def_wire_shader = self.CompileShaderProgram(def_wireshader_src)

    def GetContext(self) -> mgl.Context:
        """
        Returns handle to the active OpenGL context
        """
        return self.__ctx

    def SetViewMatrix(self, viewmat: Matrix44):
        """
        Updates active view transform matrix
        """
        self.view_matrix = viewmat.astype('float32')

    def SetPerspectiveMatrix(self, perspmat: Matrix44):
        """
        Updates active view perspective projection matrix
        """
        self.perspective_matrix = perspmat.astype('float32')

    def CompileShaderProgram(self, shader: ShaderSource) -> mgl.Program:
        """
        Compiles given shader source and returns GLSL program handle

        Passed shader source should have vertex_shader and fragment_shader defined at minimum.

        Parameters
        ----------
        shader : ShaderBase
            Shader source to comile shader program from

        Returns
        -------
        OpenGL object representation of compiled shader program
        """
        return self.GetContext().program(shader.vertex_source, shader.fragment_source)

    def ClearScreen(self, red: float, green: float, blue: float) -> None:
        """
        Redraws entire screen with given color value

        All passed color values should be normalised (0.0 - 1.0)

        Parameters
        ----------
        red : float
            Red channel color value
        green : float
            Green channel color value
        blue : float
            Blue channel color value
        """
        self.GetContext().clear(red, green, blue)

    def GenModelBuffers(self, model: RenderModel):
        """
        Generates given model buffers objects (vertex, index, etc.)

        Parameters
        ----------
        model : RenderModel
            Model to generate buffers for
        """

        # Geometry vertices & triangle indices are required
        model.vertex_buffer = self.GetContext().buffer(model.vertices)
        model.index_buffer = self.GetContext().buffer(model.indices)

        # Geometry data such as normals, texture coordinates, etc. are optional
        # When such data is not available we generated placeholder data to make
        # sure our model remains compatible with our shading pipepline.
        if len(model.normals) > 0:
            model.normal_buffer = self.GetContext().buffer(model.normals)
        else:
            size = len(model.vertices)
            dummy_normals = np.array([1.0] * size, dtype='f4')
            model.normal_buffer = self.GetContext().buffer(dummy_normals)

        if len(model.texcoords) > 0:
            model.texcoord_buffer = self.GetContext().buffer(model.texcoords)
        else:
            size = int((len(model.vertices) / 3) * 2)
            dummy_texcoords = np.array([0.0] * size, dtype='f4')
            model.texcoord_buffer = self.GetContext().buffer(dummy_texcoords)
        
        if len(model.colors) > 0:
            model.color_buffer = self.GetContext().buffer(model.colors)
        else:
            size = len(model.vertices)
            dummy_colors = np.array([1.0] * size, dtype='f4')
            model.color_buffer = self.GetContext().buffer(dummy_colors)
        self.__ValidateModelBuffers(model)

    def __ValidateModelBuffers(self, model: RenderModel) -> None:
        if model.vertex_buffer is None:
            raise Exception('Invalid vertex buffer handle!')
        if model.index_buffer is None:
            raise Exception('Invalid index buffer handle!')
        if model.normal_buffer is None:
            raise Exception('Invalid normal buffer handle!')
        if model.texcoord_buffer is None:
            raise Exception('Invalid texcoord  buffer handle!')
        if model.color_buffer is None:
            raise Exception('Invalid color  buffer handle!')

    def RenderModel(self, model: RenderModel, hints: RenderHints) -> None:
        if model is None:
            return
        
        if hints.wireframe_mode is not WireframeMode.WireframeOnly :
            self.__DrawModel(model, hints)

        if hints.wireframe_mode is WireframeMode.WireframeOnly or hints.wireframe_mode is  WireframeMode.WireframeShaded:
            self.__DrawModelWire(model, hints.wireframe_color)

    def __DrawModel(self, model: RenderModel, hints: RenderHints) -> None:
        """
        Draws given model to the screen

        Passed RenderModel should have the followinng buffers generated:
            -- Vertex Position buffer
            -- Vertex Normal buffer
            -- Index buffer

        If given model does not reference valid shader program the renderer will use
        common fallback shader (diff only)

        Parameters
        ----------
        model : RenderModel
            Model to draw to screen
        hints: RenderHints
            Flags defining rendering behaviour
        """
        transform = model.transform.GetMatrix()

        # Vertex attribute layout (pos, normal)
        attribs = [
            (model.vertex_buffer, '3f', 'in_position'),
            (model.normal_buffer, '3f', 'in_normal'),
            (model.texcoord_buffer, '2f', 'in_texcoord'),
            (model.color_buffer, '3f', 'in_color')
        ]

        shader_program = self.def_shader
        if model.shader != None:
            shader_program = model.shader

        renderable = self.GetContext().vertex_array(
            shader_program,
            attribs,
            index_buffer=model.index_buffer
        )
        
        renderable.program['modelTransform'].write(transform.tobytes())
        renderable.program['viewTransform'].write(self.view_matrix.tobytes())
        renderable.program['perspectiveTransform'].write(self.perspective_matrix.tobytes())
        renderable.program['visualise_normals'] = float(hints.visualiser_mode == VisualiserMode.ShowNormals)
        renderable.program['visualise_texcoords'] = float(hints.visualiser_mode == VisualiserMode.ShowTexcoords)
        renderable.program['visualise_colors'] = float(hints.visualiser_mode == VisualiserMode.ShowColor)
        renderable.program['light_color'] = self.light_value
        
        
        self.GetContext().wireframe = False
        self.GetContext().polygon_offset = (0,0)
        renderable.render()

    def __DrawModelWire(self, model: RenderModel, color: Vector4) -> None:
        """
        Draws given model wireframe to the screen

        Passed RenderModel should have all the buffers generated by this point.
        Passed RenderModel should have the followinng buffers generated:
            -- Vertex Position buffer
            -- Index buffer
        
        Parameters
        ----------
        model : RenderModel
            Model to draw wireframe from to screen
        coloe : Vector3
            Color (RGBA) of the wireframe lines
        """
        mat = model.transform.GetMatrix()

        # Vertex attribute layout (pos, normal)
        attribs = [
            (model.vertex_buffer, '3f', 'in_position'),
        ]

        renderable = self.GetContext().vertex_array(
            self.def_wire_shader,
            attribs,
            index_buffer=model.index_buffer
        )

        renderable.program['modelTransform'].write(mat.tobytes())
        renderable.program['viewTransform'].write(self.view_matrix.tobytes())
        renderable.program['perspectiveTransform'].write(self.perspective_matrix.tobytes())
        renderable.program['color'] = color

        self.GetContext().wireframe = True
        self.GetContext().polygon_offset = (-10,-10)
        renderable.render()

