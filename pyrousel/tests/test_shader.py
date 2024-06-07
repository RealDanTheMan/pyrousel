import os
import sys
import unittest
import importlib.resources

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyrousel.shader import ShaderSource

class ShaderTest(unittest.TestCase):
    def test_shader_loading(self):
        vertex = importlib.resources.files('pyrousel.resources.shaders').joinpath('default.vs')
        fragment = importlib.resources.files('pyrousel.resources.shaders').joinpath('default.fs')
        
        assert os.path.isfile(vertex), f'Vertex shader file not on disk -> {vertex}'
        assert os.path.isfile(vertex), f'Fragment shader file not on disk -> {fragment}'

        shader_src = ShaderSource.LoadFromFile(vertex, fragment)
        assert shader_src is not None, 'Failed to load shader source from disk!'

if __name__ == "__main__":
    unittest.main()