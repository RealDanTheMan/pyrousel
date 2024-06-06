import os
import sys
import unittest
import importlib.resources
import glfw
import moderngl as mgl

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyrousel.gfx import GFX, MaterialSettings, RenderHints, WireframeMode
from pyrousel.shader import ShaderSource
from pyrousel.model import ModelLoader

class GFXTest(unittest.TestCase):
    def test_glcontext(self):
        '''
        Tests the creation of dummy OpenGL context

        Dummy OpenGL context is needed for all the tests performed on the graphics
        '''
        # Create dummy OpenGL context
        ctx = self.__CreateDummyContext()
        assert ctx is not None, 'Failed to create dummy OpenGL context!'

        # Dispose of the dummy OpenGL context
        self.__DestroyDummyContext()

    def test_default_shader(self):
        # Create dummy OpenGL context
        ctx = self.__CreateDummyContext()
        assert ctx is not None, 'Failed to create dummy OpenGL context!'

        # Locate and validate shader source files
        vertex = importlib.resources.files('pyrousel.resources.shaders').joinpath('default.vs')
        fragment = importlib.resources.files('pyrousel.resources.shaders').joinpath('default.fs')
        assert os.path.isfile(vertex), f'Vertex shader file not on disk -> {vertex}'
        assert os.path.isfile(vertex), f'Fragment shader file not on disk -> {fragment}'

        # Load shader source files
        shader_src = ShaderSource.LoadFromFile(vertex, fragment)
        assert shader_src is not None, 'Failed to load shader source from disk!'

        # Initialise and validate graphics
        gfx = GFX(ctx)
        assert gfx is not None
        
        # Compile and validate shader program
        shader = gfx.CompileShaderProgram(shader_src)
        assert shader is not None

        # Dispose of the dummy OpenGL context
        self.__DestroyDummyContext()

    def test_wireframe_shader(self):
        # Create dummy OpenGL context
        ctx = self.__CreateDummyContext()
        assert ctx is not None, 'Failed to create dummy OpenGL context!'

        # Locate and validate shader source files
        vertex = importlib.resources.files('pyrousel.resources.shaders').joinpath('wireframe.vs')
        fragment = importlib.resources.files('pyrousel.resources.shaders').joinpath('wireframe.fs')
        assert os.path.isfile(vertex), f'Vertex shader file not on disk -> {vertex}'
        assert os.path.isfile(vertex), f'Fragment shader file not on disk -> {fragment}'

        # Load shader source files
        shader_src = ShaderSource.LoadFromFile(vertex, fragment)
        assert shader_src is not None, 'Failed to load shader source from disk!'

        # Initialise and validate graphics
        gfx = GFX(ctx)
        assert gfx is not None
        
        # Compile and validate shader program
        shader = gfx.CompileShaderProgram(shader_src)
        assert shader is not None

        # Dispose of the dummy OpenGL context
        self.__DestroyDummyContext()

    def test_model_buffergen(self):
        # Create dummy OpenGL context
        ctx = self.__CreateDummyContext()
        assert ctx is not None, 'Failed to create dummy OpenGL context!'

        # Load model source
        model_filepath = importlib.resources.files('resources.models.gltf').joinpath('monkey.glb')
        assert os.path.isfile(model_filepath), f'Model file not on disk -> {model_filepath}'
        
        # Interpret model data
        model = ModelLoader.LoadModel(model_filepath)
        assert model is not None, f'Failed to load model -> {model_filepath}'

        # Initialise and validate graphics
        gfx = GFX(ctx)
        assert gfx is not None

        # Generate and validate model buffers
        gfx.GenModelBuffers(model)
        assert model.vertex_buffer is not None, 'Invalid model vertex buffer!'
        assert model.normal_buffer is not None, 'Invalid model surface normal buffer!'
        assert model.texcoord_buffer is not None, 'Invalid model texture coordinate buffer!'
        assert model.color_buffer is not None, 'Invalid model vertex color buffer!'
        assert model.index_buffer is not None, 'Invalid model vertex index buffer!'

        # Dispose of the dummy OpenGL context
        self.__DestroyDummyContext()

    def test_model_render(self):
        # Create dummy OpenGL context
        ctx = self.__CreateDummyContext()
        assert ctx is not None, 'Failed to create dummy OpenGL context!'

        # Load model source
        model_filepath = importlib.resources.files('resources.models.gltf').joinpath('monkey.glb')
        assert os.path.isfile(model_filepath), f'Model file not on disk -> {model_filepath}'
        
        # Interpret model data
        model = ModelLoader.LoadModel(model_filepath)
        assert model is not None, f'Failed to load model -> {model_filepath}'

        # Initialise and validate graphics
        gfx = GFX(ctx)
        assert gfx is not None

        # Generate and validate model buffers
        gfx.GenModelBuffers(model)

        mat = MaterialSettings()
        hints = RenderHints()
        hints.wireframe_mode = WireframeMode.WireframeShaded

        # Clear screen and render the model
        gfx.ClearScreen(0,0,0)
        gfx.RenderModel(model, hints, mat)

        # Dispose of the dummy OpenGL context
        self.__DestroyDummyContext()

    def __CreateDummyContext(self):
        if not glfw.init():
            return None
        win = glfw.create_window(512, 512, "Test", None, None)
        if win is None:
            self.__DestroyDummyContext()
            return None
        glfw.make_context_current(win)
        ctx = mgl.create_context()

        return ctx

    def __DestroyDummyContext(self):
        glfw.terminate()

if __name__ == "__main__":
    unittest.main()