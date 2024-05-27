import glfw
import moderngl as mgl
import moderngl_window as mglwin
import numpy as np
import math
from pyrr import vector3, Vector3
from pyrousel.appgui import AppGUI
from pyrousel.gfx import GFX
from pyrousel.shader import ShaderFallback
from pyrousel.model import RenderModel, PrimitiveFactory, ModelLoader
from pyrousel.camera import Camera

class AppWindow(object):
    def __init__(self, width: int = 1280, height: int = 720):
        self.__width = width
        self.__height = height
        self.__aspec_ratio = self.__width / self.__height
        self.draw_wireframe = False
        self.draw_shaded = True
        self.enable_carousel = True
        
        # Initialise GLFW window & OpenGL context
        if not glfw.init():
            raise Exception("GLFW failed to initialise!")
        
        self.__win = glfw.create_window(width, height, "Window Label", None, None)
        if not self.__win:
            glfw.terminate()
            raise Exception("GLFW Window failed to initialise properly!")
        else:
            glfw.make_context_current(self.__win)

        # App user interface (IMGui)
        self.gui = AppGUI(self.__win)
        self.gui.import_settings.ModelRequestSignal.connect(self.OnModelRequested)
        self.gui.import_settings.ModelReloadSignal.connect(self.OnModelReloadRequested)
        self.gui.camera_settings.CameraFocusRequested.connect(self.OnCameraFocusRequested)

    def Init(self) -> None:
        """Initialises OpenGL graphics renderer"""
        self.graphics = GFX(mgl.create_context())

        self.__LoadModel('resources/models/obj/ChessKing.obj')
        self.camera = Camera()
        self.camera.aspect = self.__aspec_ratio
        self.camera.transform.Translate(0.0, 0.0, 5.0)
        self.__FrameModel()
        self.__UpdateUI()

    def OnModelRequested(self, earg: str) -> None:
        """Event handler for loading new model into the scene"""
        if not earg is None and earg is not self.model_filepath:
            print(f'Loading model: {earg}')
            self.model_filepath = earg
            self.__LoadModel(earg)
            self.__FrameModel()

    def OnModelReloadRequested(self, earg) -> None:
        """Event handler for reloading active model in the current scene"""
        if not self.model_filepath is None:
            print(f'Reloading active model')
            self.__LoadModel(self.model_filepath)
            self.__FrameModel()

    def OnCameraFocusRequested(self, earg) -> None:
        """Event handler for camera model focus"""
        print(f'Requesting model camera focus')
        self.__FrameModel()

    def __LoadModel(self, filepath: str) -> None:
        """Loads given model into the active scene"""
        self.model_filepath = filepath
        self.model = ModelLoader.LoadFromOBJ(filepath)
        self.model.RecomputeBounds()
        self.graphics.GenModelBuffers(self.model)

    def __FrameModel(self) -> None:
        """Aligns the camera so that the loaded model is in a full view"""
        if not self.model is None:
            minext = self.model.transform.GetMatrix() * self.model.minext
            maxext = self.model.transform.GetMatrix() * self.model.maxext
            center = (minext + maxext) * 0.5
            size = vector3.length(maxext - center)
            rfov = math.radians(self.camera.fov)
            radius = (size * 0.5) / math.tan(rfov * 0.5)
            pos = center - Vector3([0.0, 0.0, -1.0]) * (radius * 2.0)
            self.camera.transform.SetTranslation(pos.x, pos.y, pos.z)

    def __UpdateUI(self) -> None:
        """Updates various UI properties"""
        self.gui.import_settings.model_filepath = self.model_filepath
        self.gui.scene_stats.num_vertex = len(self.model.vertices) / 3
        self.gui.scene_stats.num_triangles = len(self.model.indices) / 3
        self.gui.scene_stats.min_ext = self.model.minext
        self.gui.scene_stats.max_ext = self.model.maxext
        
        self.gui.camera_settings.fov = self.camera.fov
        self.gui.camera_settings.near_plane = self.camera.near_clip
        self.gui.camera_settings.far_plane = self.camera.far_clip
        
        self.gui.transforms.spin_model = self.enable_carousel
        translation = self.model.transform.GetTranslation()
        self.gui.transforms.translation[0] = translation.x
        self.gui.transforms.translation[1] = translation.y
        self.gui.transforms.translation[2] = translation.z
        rotation = self.model.transform.GetRotation()
        self.gui.transforms.rotation[0] = np.degrees(rotation.x)
        self.gui.transforms.rotation[1] = np.degrees(rotation.y)
        self.gui.transforms.rotation[2] = np.degrees(rotation.z)
        scale = self.model.transform.GetScale()
        self.gui.transforms.scale[0] = scale.x
        self.gui.transforms.scale[1] = scale.y
        self.gui.transforms.scale[2] = scale.z

    def __FetchUI(self) -> None:
        """Fetches property values from UI that influence the app behaviour"""
        if self.gui.overlays.wireframe_only:
            self.draw_shaded = False
            self.draw_wireframe = True
        elif self.gui.overlays.wireframe_shaded:
            self.draw_shaded = True
            self.draw_wireframe = True
        else:
            self.draw_shaded = True
            self.draw_wireframe = False

        self.camera.fov = self.gui.camera_settings.fov
        self.camera.near_clip = self.gui.camera_settings.near_plane
        self.camera.far_clip = self.gui.camera_settings.far_plane

        self.enable_carousel = self.gui.transforms.spin_model
        if not self.model is None:
            tr_x = self.gui.transforms.translation[0]
            tr_y = self.gui.transforms.translation[1]
            tr_z = self.gui.transforms.translation[2]
            self.model.transform.SetTranslation(tr_x, tr_y, tr_z)

            if not self.enable_carousel:
                rot_x = np.radians(self.gui.transforms.rotation[0])
                rot_y = np.radians(self.gui.transforms.rotation[1])
                rot_z = np.radians(self.gui.transforms.rotation[2])
                self.model.transform.SetRotation(rot_x, rot_y, rot_z)
            
            scale_x = self.gui.transforms.scale[0]
            scale_y = self.gui.transforms.scale[1]
            scale_z = self.gui.transforms.scale[2]
            self.model.transform.SetScale(scale_x, scale_y, scale_z)

    def __UpdateScene(self) -> None:
        """Updates the scene"""
        if self.model and self.enable_carousel:
            self.model.transform.Rotate(0.0, 0.02, 0.0)

    def __RenderScene(self) -> None:
        """Draws active scene content to the screen"""
        self.graphics.ClearScreen(0.1, 0.1, 0.1)
        self.graphics.SetViewMatrix(self.camera.GetViewMatrix())
        self.graphics.SetPerspectiveMatrix(self.camera.GetPerspectiveMatrix())

        if self.draw_shaded:
            self.graphics.DrawModel(self.model)
        if self.draw_wireframe:
            self.graphics.DrawModelWire(self.model)

        self.gui.Render()
        glfw.swap_buffers(self.__win)

    def Run(self) -> None:
        """Updates & Draw active scene continusely until window closes"""
        while not glfw.window_should_close(self.__win):
            glfw.poll_events()
            self.__FetchUI()
            self.__UpdateUI()
            self.__UpdateScene()
            self.__RenderScene()

    def Quit(self):
        self.gui.Shutdown()
        glfw.terminate()