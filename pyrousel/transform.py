import numpy as np
from pyrr import Matrix44, Vector3, quaternion

class Transform(object):
    def __init__(self):
        self.__tr: Matrix44 = Matrix44.identity()
        self.__rot_x: Matrix44 = Matrix44.identity()
        self.__rot_y: Matrix44 = Matrix44.identity()
        self.__rot_z: Matrix44 = Matrix44.identity()
        self.__scale: Matrix44 = Matrix44.identity()
        self.__final: Matrix44 = Matrix44.identity()
        self.__dirty: bool = False
    
    def GetMatrix(self) -> Matrix44:
        """ Returns composite transform matrix """
        if self.__dirty:
            self.__RecomputeMatrix()
        return self.__final.astype('float32')

    def Translate(self, x: float, y: float, z: float) -> None:
        """
        Applies given translation to the existing transform

        Parameters
        ----------
        x : float
            Translation value along the X axis

        y : float
            Translation value along the Y axis

        z : float
            Translation value along the Z axis

        """
        tr_mat = Matrix44.from_translation(Vector3([x, y, z]))
        self.__tr *= tr_mat
        self.__dirty = True

    def SetTranslation(self, x: float, y: float, z: float) -> None:
        """Overrides current transform translation"""
        self.__tr = Matrix44.from_translation(Vector3([x, y, z]))
        self.__dirty = True

    def Rotate(self, x: float, y: float, z: float) -> None:
        """
        Applies given rotation to the existing transform

        Parameters
        ----------
        x : float
            Rotation along the X axis in radians

        y : float
            Rotation along the Y axis in radians

        z : float
            Rotation along the Z axis in radians

        """
        x_mat = Matrix44.from_x_rotation(x)
        y_mat = Matrix44.from_y_rotation(y)
        z_mat = Matrix44.from_z_rotation(z)

        self.__rot_x *= x_mat
        self.__rot_y *= y_mat
        self.__rot_z *= z_mat
        self.__dirty = True

    def SetRotation(self, x: float, y: float, z: float):
        """
        Overrides current transform rotation

        Parameters
        ----------
        x : float
            Rotation along the X axis in radians

        y : float
            Rotation along the Y axis in radians

        z : float
            Rotation along the Z axis in radians
        """
        self.__rot_x = Matrix44.from_x_rotation(x)
        self.__rot_y = Matrix44.from_y_rotation(y)
        self.__rot_z = Matrix44.from_z_rotation(z)
        self.__dirty = True

    def Scale(self, x: float, y: float, z: float) -> None:
        """
        Applies given scale to the existing transform

        Parameters
        ----------
        x : float
            Scale along the X axis

        y : float
            Scale along the Y axis

        z : float
            Scale along the Z axis

        """
        scale_mat = Matrix44.from_scale(Vector3([x, y, z]))
        self.__scale *= scale_mat
        self.__dirty = True

    def SetScale(self, x: float, y: float, z: float) -> None:
        """Overrides current transform scale"""
        self.__scale = Matrix44.from_scale(Vector3([x, y, z]))
        self.__dirty = True

    def __RecomputeMatrix(self) -> None:
        """ Recalculates internal composite transform matrix """
        self.__final = self.__tr * self.__rot_x * self.__rot_y * self.__rot_z * self.__scale

    def GetTranslation(self) -> Vector3:
        """ Returns current translation """
        x = self.__tr[3,0]
        y = self.__tr[3,1]
        z = self.__tr[3,2]

        return Vector3([x, y, z])

    def GetRotation(self) -> Vector3:
        """Returns current rotation"""
        xQuat = self.__rot_x.decompose()[1]
        yQuat = self.__rot_y.decompose()[1]
        zQuat = self.__rot_z.decompose()[1]

        return Vector3([
            quaternion.rotation_angle(xQuat),
            quaternion.rotation_angle(yQuat),
            quaternion.rotation_angle(zQuat)
        ])

        xangle = euler.matrx44.to_eulers(xrot)
        yangle = euler.Matrix44(xrot).angles[0]
        zangle = euler.Matrix44(xrot).angles[0]

        return Vector3([xangle, yangle, zangle])

    def GetScale(self) -> Vector3:
        """ Returns current scale """
        x = self.__scale[0,0]
        y = self.__scale[1,1]
        z = self.__scale[2,2]

        return Vector3([x, y, z])