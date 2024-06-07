from __future__ import annotations

class ShaderSource(object):
    def __init__(self):
        self.vertex_source = None
        self.fragment_source = None

    @staticmethod
    def LoadFromFile(vertexFilepath: str, fragmentFilepath: str) -> ShaderSource:
        """
        Return shader source object representing shader code from disk

        Parameters
        ----------
        vertexFilepath : str
            Filepath to file containing vertex shader source
        fragmentFilepath : str
            Filepath to file containing fragment shader source
        """
        shader = ShaderSource()
        with open(vertexFilepath, 'r') as file:
            shader.vertex_source = file.read()
        with open(fragmentFilepath, 'r') as file:
            shader.fragment_source = file.read() 
        return shader