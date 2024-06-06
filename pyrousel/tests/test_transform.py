import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyrousel.transform import Transform
from pyrr import Vector3

class TransformTest(unittest.TestCase):
    def test_position(self):
        pos = Vector3([10.0, 20.0, 30.0])
        transform = Transform()
        transform.Translate(pos.x, pos.y, pos.z)

        assert transform.GetTranslation() == pos

        transform.SetTranslation(0.0, 0.0, 0.0)
        transform.SetTranslation(pos.x, pos.y, pos.z)

        assert transform.GetTranslation() == pos

    def test_scale(self):
        scale = Vector3([2.0, 3.0, 4.0])
        transform = Transform()
        transform.Scale(scale.x, scale.y, scale.z)

        assert transform.GetScale() == scale

        transform.SetScale(0.0, 0.0, 0.0)
        transform.SetScale(scale.x, scale.y, scale.z)

        assert transform.GetScale() == scale



if __name__ == "__main__":
    unittest.main()