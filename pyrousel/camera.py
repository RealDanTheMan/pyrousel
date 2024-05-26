import numpy as np
from pyrr import Matrix44, Vector3
from pyrousel.transform import Transform

class Camera(object):
    def __init__(self):
        self.transform: Transform = Transform()
        self.perspective: Matrix44 = Matrix44.identity()
        self.up: Vector3 = Vector3([0.0, 1.0, 0.0])
        self.near_clip: float = 0.001
        self.far_clip: float = 1000000.0
        self.fov = 60.0
        self.aspect = 16 / 9

    def GetViewMatrix(self) -> Matrix44:
        """ Returns camera view transform matrix"""
        return Matrix44.look_at(
            self.transform.GetTranslation(),
            self.transform.GetTranslation() + Vector3([0.0, 0.0, -10000000.0]), 
            self.up
        )

    def GetPerspectiveMatrix(self) -> Matrix44:
        """ Returns camera perspective projection matrix"""
        return Matrix44.perspective_projection(
            self.fov,
            self.aspect,
            self.near_clip,
            self.far_clip
        )