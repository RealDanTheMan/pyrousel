import time
import importlib.resources
import glfw
import moderngl as mgl
import numpy as np
import math
from pyrr import vector3, Vector3, Vector4

from .appgui import AppGUI
from .gfx import GFX, RenderHints, MaterialSettings
from .model import ModelLoader
from .camera import Camera

class AppWindow(object):
    def __init__(self, width: int = 1280, height: int = 720, enable_gui=True):
        self.__width = width
        self.__height = height
        self.__aspec_ratio = self.__width / self.__height
        self.render_hints = RenderHints()
        self.render_hints.wireframe_color = Vector4([0.0, 0.55, 0.0, 0.22])
        self.material_settings = MaterialSettings()
        self.material_settings.base_color = Vector3([0.615, 0.28, 0.18])
        self.material_settings.roughness = 0.5
        self.material_settings.spec_intensity = 0.7
        self.enable_carousel = True
        self.frame_counter = FrameCounter()
        self.frame_counter.Start()
        self.light_color = Vector3([1,1,1])
        self.light_intensity = 1.0
        
        # Initialise GLFW window & OpenGL context
        if not glfw.init():
            raise Exception("GLFW failed to initialise!")
        
        self.__win = glfw.create_window(width, height, "Window Label", None, None)
        if not self.__win:
            glfw.terminate()
            raise Exception("GLFW Window failed to initialise properly!")
        else:
            glfw.make_context_current(self.__win)
            glfw.set_key_callback(self.__win, self.OnKeyCallback)
            glfw.swap_interval(0)

        # App user interface (IMGui)
        if enable_gui:
            self.gui = AppGUI(self.__win)
            self.gui.import_settings.ModelRequestSignal.connect(self.OnModelRequested)
            self.gui.import_settings.ModelReloadSignal.connect(self.OnModelReloadRequested)
            self.gui.camera_settings.CameraFocusRequested.connect(self.OnCameraFocusRequested)
            self.draw_gui = True
        else:
            self.gui = None
            self.draw_gui = False

    def Init(self) -> None:
        """Initialises OpenGL graphics renderer"""
        self.graphics = GFX(mgl.create_context())
        self.camera = Camera()
        self.camera.aspect = self.__aspec_ratio
        self.camera.fov = 30.0
        self.camera.transform.Translate(0.0, 0.0, 5.0)  

        with importlib.resources.path('pyrousel.resources.models.obj', 'monkey.obj') as startup_model:
            self.__LoadModel(startup_model)
        
        self.__FrameModel()
        self.__UpdateUI()

    def OnModelRequested(self, earg: str) -> None:
        """Event handler for loading new model into the scene"""
        if earg is not None and earg is not self.model_filepath:
            print(f'Loading model: {earg}')
            self.model_filepath = earg
            self.__LoadModel(earg)
            self.__FrameModel()

    def OnModelReloadRequested(self, earg) -> None:
        """Event handler for reloading active model in the current scene"""
        if self.model_filepath is not None:
            print('Reloading active model')
            self.__LoadModel(self.model_filepath)
            self.__FrameModel()

    def OnCameraFocusRequested(self, earg) -> None:
        """Event handler for camera model focus"""
        print('Requesting model camera focus')
        self.__FrameModel()

    def __LoadModel(self, filepath: str) -> None:
        """Loads given model into the active scene"""
        self.model_filepath = filepath
        self.model = ModelLoader.LoadModel(filepath)
        self.model.RecomputeBounds()
        self.graphics.GenModelBuffers(self.model)

    def __FrameModel(self) -> None:
        """Aligns the camera so that the loaded model is in a full view"""
        if self.model is not None:
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
        if self.gui is None:
            return

        self.gui.import_settings.model_filepath = self.model_filepath
        self.gui.scene_stats.num_vertex = len(self.model.vertices) / 3
        self.gui.scene_stats.num_triangles = len(self.model.indices) / 3
        self.gui.scene_stats.min_ext = self.model.minext
        self.gui.scene_stats.max_ext = self.model.maxext
        self.gui.scene_stats.fps = self.frame_counter.GetFPS()
        self.gui.scene_stats.frame_time = self.frame_counter.GetFrameTime()
        self.gui.scene_stats.frames = self.frame_counter.GetFrames()

        self.gui.overlays.wireframe_mode = self.render_hints.wireframe_mode
        self.gui.overlays.visualise_state = self.render_hints.visualiser_mode
        self.gui.overlays.wireframe_color = list(self.render_hints.wireframe_color)

        self.gui.material_settings.color = list(self.material_settings.base_color)
        self.gui.material_settings.rougness = self.material_settings.roughness
        self.gui.material_settings.specular = self.material_settings.spec_intensity
        self.gui.material_settings.F0 = self.material_settings.F0
        
        self.gui.camera_settings.fov = self.camera.fov
        self.gui.camera_settings.near_plane = self.camera.near_clip
        self.gui.camera_settings.far_plane = self.camera.far_clip

        self.gui.light_settings.light_color = list(self.light_color)
        self.gui.light_settings.light_intensity = self.light_intensity
        
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
        if self.gui is None:
            return

        self.render_hints.visualiser_mode = self.gui.overlays.visualiser_mode
        self.render_hints.wireframe_mode = self.gui.overlays.wireframe_mode
        self.render_hints.wireframe_color = Vector4(self.gui.overlays.wireframe_color)

        self.material_settings.base_color = Vector3(self.gui.material_settings.color)
        self.material_settings.roughness = self.gui.material_settings.rougness
        self.material_settings.spec_intensity = self.gui.material_settings.specular
        self.material_settings.F0 = self.gui.material_settings.F0

        self.camera.fov = self.gui.camera_settings.fov
        self.camera.near_clip = self.gui.camera_settings.near_plane
        self.camera.far_clip = self.gui.camera_settings.far_plane
        self.light_color = Vector3(self.gui.light_settings.light_color)
        self.light_intensity = self.gui.light_settings.light_intensity

        self.enable_carousel = self.gui.transforms.spin_model
        if self.model is not None:
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
        self.__ProcessInputs()
        if self.model and self.enable_carousel:
            self.model.transform.Rotate(0.0, 0.02, 0.0)

    def __RenderScene(self) -> None:
        """Draws active scene content to the screen"""
        self.graphics.ClearScreen(0.1, 0.1, 0.1)
        self.graphics.SetViewMatrix(self.camera.GetViewMatrix())
        self.graphics.SetPerspectiveMatrix(self.camera.GetPerspectiveMatrix())
        self.graphics.light_value = self.light_color * self.light_intensity
        self.graphics.RenderModel(self.model, self.render_hints, self.material_settings)
        
        if self.gui is not None and self.draw_gui:
            self.gui.Render()
        
        glfw.swap_buffers(self.__win)

    def __ProcessInputs(self) -> None:
        """Process window key and mouse inputs"""
        glfw.poll_events()
        if self.gui is not None and self.draw_gui:
            self.gui.ProcessInputs()

    def Run(self) -> None:
        """Updates & Draw active scene continusely until window closes"""
        while not glfw.window_should_close(self.__win):
            self.__FetchUI()
            self.__UpdateUI()
            self.__UpdateScene()
            self.__RenderScene()
            self.frame_counter.Update()

    def OnKeyCallback(self, window, key, scancode, action, mods) -> None:
        """Event handler for GLFW key input callbacks"""
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)

        if key == glfw.KEY_X and action == glfw.PRESS:
            self.draw_gui = not self.draw_gui

    def Quit(self) -> None:
        self.gui.Shutdown()
        glfw.terminate()

class FrameCounter(object):
    def __init__(self, max_samples: int  = 32):
        self.__current: float = 0.0
        self.__last: float = 0.0
        self.__frames: int = 0
        self.__frameTime: float = 0.0
        self.__fps: int = 0
        self.__max_samples: int = max_samples
        self.__samples: list(float) = [0] * self.__max_samples
        self.__sample_idx: int = 0

    def Start(self) -> None:
        """Start/Restart the timer"""
        self.__current: float = 0.0
        self.__last: float = 0.0
        self.__frames: int = 0
        self.__fps: int = 0
        self.__samples = [0] * self.__max_samples
        self.__sample_idx: int = 0

    def Update(self) -> None:
        """Take a frame time sample and update FPS and frame count"""
        self.__last = self.__current
        self.__current = time.time()
        self.__samples[self.__sample_idx] = self.__current - self.__last
        self.__frames += 1

        sample_time = (sum(self.__samples) / self.__max_samples)
        self.__frameTime = sample_time * 1000.0
        self.__fps = int(1.0 / sample_time)

        if self.__sample_idx < self.__max_samples - 1:
            self.__sample_idx += 1
        else:
            self.__sample_idx = 0

    def GetFPS(self) -> int:
        """Returns current FPS"""
        return int(self.__fps)

    def GetFrames(self) -> int:
        """Returns frame count since the counter start"""
        return self.__frames

    def GetFrameTime(self) -> float:
        """Returns average frame timein milliseconds across all the samples"""
        return self.__frameTime
