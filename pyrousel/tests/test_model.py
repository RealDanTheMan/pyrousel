import os
import sys
import unittest
import importlib.resources
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyrousel.model import Model, ModelLoader
from pyrr import Vector3

class ModelTest(unittest.TestCase):
    def test_obj_loading(self):
        # Locate and validate model file
        model_filepath = importlib.resources.files('resources.models.obj').joinpath('monkey.obj')
        assert os.path.isfile(model_filepath), f'Model file not on disk -> {model_filepath}'
        
        # Load the model and validate its contents
        model = ModelLoader.LoadModel(model_filepath)
        ModelTest.__ValidateModelContents(model)


    def test_gltf_loading(self):
        # Locate and validate model file
        model_filepath = importlib.resources.files('resources.models.gltf').joinpath('monkey.glb')
        assert os.path.isfile(model_filepath), f'Model file not on disk -> {model_filepath}'

        # Load the model and validate its contents
        model = ModelLoader.LoadModel(model_filepath)
        ModelTest.__ValidateModelContents(model)

    def test_collada_loading(self):
        # Locate and validate model file
        model_filepath = importlib.resources.files('resources.models.collada').joinpath('monkey.dae')
        assert os.path.isfile(model_filepath), f'Model file not on disk -> {model_filepath}'

        # Load the model and validate its contents
        model = ModelLoader.LoadModel(model_filepath)
        ModelTest.__ValidateModelContents(model)

    @staticmethod
    def __ValidateModelContents( model: Model) -> None:
        assert model is not None, 'Model loading resulted in invalid model object!'
        assert len(model.vertices) > 0, 'Loaded model has no vertex data!'
        assert len(model.normals) > 0, 'Loaded model has no surface normal data!'
        assert len(model.texcoords) > 0, 'Loaded model has no texture coordinate data!'
        assert len(model.indices) > 0, 'Loaded model has no vertex indices data!'

        # At this point in time vertex color is not well supported yet.
        #assert len(model.colors) > 0, 'Loaded model has no vertex color data!'

        model.RecomputeBounds()
        min = model.minext
        max = model.maxext
        assert not np.array_equal(min, Vector3([0.0, 0.0, 0.0])), 'Model has invalid minimum extends!'
        assert not np.array_equal(max, Vector3([0.0, 0.0, 0.0])), 'Model has invalid maximum extends!'

        valid_extends = min.x < max.x and min.y < max.y and min.z < max.z
        assert valid_extends, 'Model extends are invalid!'

if __name__ == "__main__":
    unittest.main()