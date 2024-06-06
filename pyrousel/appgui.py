import os
import importlib.resources
import easygui
import imgui
from imgui.integrations.glfw import GlfwRenderer as IMRenderer
from glfw import _GLFWwindow
from blinker import Signal

from .gfx import VisualiserMode, WireframeMode

class AppGUI(object):
    def __init__(self, win_handle: _GLFWwindow):
        imgui.create_context()
        self.__impl = IMRenderer(win_handle)
        self.import_settings = ImportSettingsPanel()
        self.scene_stats = SceneStatsPanel()
        self.overlays = OverlaysPanel()
        self.camera_settings = CameraSettingsPanel()
        self.material_settings = MaterialSettingsPanel()
        self.light_settings = LightSettingsPanel()
        self.transforms = TransformsPanel()

    def __ProcessInputs(self) -> None:
        imgui.capture_mouse_from_app(True)
        self.__impl.process_inputs()

    def __Update(self) -> None:
        """Process GUI inputs and builds UI widgets"""
        self.__ProcessInputs()
        
        imgui.new_frame()
        imgui.begin("Property Panel")
        self.import_settings.Update()
        self.scene_stats.Update()
        self.overlays.Update()
        self.material_settings.Update()
        self.camera_settings.Update()
        self.light_settings.Update()
        self.transforms.Update()
        imgui.end()

    def __Draw(self) -> None:
        """Draw GUI to the screen"""
        imgui.render()
        self.__impl.render(imgui.get_draw_data())

    def Render(self) -> None:
        """Redrawing the GUI widgets"""
        self.__Update()
        self.__Draw()

    def Shutdown(self) -> None:
        """Free up any resources and terminate IMGui renderer"""
        self.__impl.shutdown()

class SceneStatsPanel(object):
    def __init__(self):
        self.fps = 0
        self.frames = 0
        self.num_vertex: int = 0
        self.num_triangles: int = 0
        self.min_ext = [0.0, 0.0, 0.0]
        self.max_ext = [0.0, 0.0, 0.0]

    def Update(self) -> None:
        """Builds IMGui widgest that make this panel"""
        if imgui.collapsing_header("Scene Settings")[0]:
            imgui.begin_child("#Scene Settings Panel", width=0, height=150, border=True)
            imgui.text('FPS: ')
            imgui.same_line(position=200)
            imgui.input_int('##FPS', self.fps, flags=imgui.INPUT_TEXT_READ_ONLY)
            imgui.text('Frames: ')
            imgui.same_line(position=200)
            imgui.input_int('##Frame', self.frames, flags=imgui.INPUT_TEXT_READ_ONLY)
            imgui.text('Vertices: ')
            imgui.same_line(position=200)
            imgui.input_int('##Vertex Count', self.num_vertex, flags=imgui.INPUT_TEXT_READ_ONLY)
            imgui.text('Triangles: ')
            imgui.same_line(position=200)
            imgui.input_int('##Triangle Count', self.num_triangles, flags=imgui.INPUT_TEXT_READ_ONLY)
            imgui.text('Min Extends: ')
            imgui.same_line(position=200)
            imgui.input_float3(
                '##Min Extends',
                self.min_ext[0],
                self.min_ext[1],
                self.min_ext[2],
                flags=imgui.INPUT_TEXT_READ_ONLY
            )

            imgui.text('Max Extends: ')
            imgui.same_line(position=200)
            imgui.input_float3(
                '##Max Extends',
                self.max_ext[0],
                self.max_ext[1],
                self.max_ext[2],
                flags=imgui.INPUT_TEXT_READ_ONLY
            )
            
            imgui.end_child()

class OverlaysPanel(object):
    def __init__(self):
        self.visualiser_mode = VisualiserMode.ShowDefault
        self.wireframe_mode = WireframeMode.WireframeOff
        self.wireframe_color = [1.0, 1.0, 1.0, 1.0]

    def Update(self) -> None:
        """Builds IMGui widgest that make this panel"""
        if imgui.collapsing_header("Overlay Settings")[0]:
            imgui.begin_child("#Overlay Settings Panel", width=0, height=240, border=True)
            imgui.text('Wireframe:')
            imgui.separator()
            imgui.dummy(0, 5)
            imgui.text('Wireframe Off:')
            imgui.same_line(position=200)
            if imgui.radio_button("##Wireframe Off", self.wireframe_mode == WireframeMode.WireframeOff):
                self.wireframe_mode = WireframeMode.WireframeOff
            imgui.text('Wireframe Only:')
            imgui.same_line(position=200)
            if imgui.radio_button("##Wireframe Only", self.wireframe_mode == WireframeMode.WireframeOnly):
                self.wireframe_mode = WireframeMode.WireframeOnly
            imgui.text('Wireframe Shaded:')
            imgui.same_line(position=200)
            if imgui.radio_button("##Wireframe Shaded", self.wireframe_mode == WireframeMode.WireframeShaded):
                self.wireframe_mode = WireframeMode.WireframeShaded
            
            imgui.text('Wireframe Color:')
            imgui.same_line(position=200)
            _, self.wireframe_color = imgui.input_float4(
                '##Wireframe color',
                self.wireframe_color[0],
                self.wireframe_color[1],
                self.wireframe_color[2],
                self.wireframe_color[3]
            )
            imgui.dummy(0, 5)
            imgui.text('Visualisers:')
            imgui.separator()
            imgui.dummy(0, 5)
            imgui.text('Show Default:')
            imgui.same_line(position=200)
            if imgui.radio_button("##Show Default", self.visualiser_mode == VisualiserMode.ShowDefault):
                self.visualiser_mode = VisualiserMode.ShowDefault
            imgui.text('Show Normals:')
            imgui.same_line(position=200)
            if imgui.radio_button("##Show Normals", self.visualiser_mode == VisualiserMode.ShowNormals):
                self.visualiser_mode = VisualiserMode.ShowNormals
            imgui.text('Show Texcoords:')
            imgui.same_line(position=200)
            if imgui.radio_button("##Show Texcoords", self.visualiser_mode == VisualiserMode.ShowTexcoords):
                self.visualiser_mode = VisualiserMode.ShowTexcoords
            imgui.text('Show Color:')
            imgui.same_line(position=200)
            if imgui.radio_button("##Show Color", self.visualiser_mode == VisualiserMode.ShowColor):
                self.visualiser_mode = VisualiserMode.ShowColor
            imgui.end_child()

class ImportSettingsPanel(object):
    def __init__(self):
        self.model_filepath = None
        self.ModelRequestSignal = Signal()
        self.ModelReloadSignal = Signal()

    def Update(self):
        if imgui.collapsing_header("Import Settings")[0]:
            max_width = imgui.get_content_region_available_width()
            imgui.begin_child("#Import Settings Panel", width=0, height=75, border=True)
            imgui.text(str(os.path.basename(self.model_filepath)))
            if imgui.button('Load Model', width=max_width):
                dir = importlib.resources.files('pyrousel.resources.models.obj').joinpath('monkey.obj')
                print('default file')
                print(dir)
                self.model_filepath = easygui.fileopenbox(default=dir)
                self.ModelRequestSignal.send(self.model_filepath)
            if imgui.button('Reload', width=max_width):
                self.ModelReloadSignal.send(None)
            imgui.end_child()

class TransformsPanel(object):
    def __init__(self):
        self.spin_model = True
        self.translation = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0]
        self.scale = [1.0, 1.0, 1.0]

    def Update(self):
        """Builds IMGui widgest that make this panel"""
        if imgui.collapsing_header("Transform")[0]:
            imgui.begin_child("#Transform Settings Panel", width=0, height=320, border=True)
            imgui.text('Enable Carousel:')
            imgui.same_line(position=200)
            _, self.spin_model = imgui.checkbox('##Spin Model', self.spin_model)
            
            imgui.separator()
            imgui.text('Translation:')
            imgui.text('x:')
            imgui.same_line(position=50)
            _, self.translation[0] = imgui.input_float('##Translation x', self.translation[0])
            imgui.text('y:')
            imgui.same_line(position=50)
            _, self.translation[1] = imgui.input_float('##Translation y', self.translation[1])
            imgui.text('z:')
            imgui.same_line(position=50)
            _, self.translation[2] = imgui.input_float('##Translation z', self.translation[2])
            
            imgui.separator()
            imgui.text('Rotation:')
            imgui.text('x:')
            imgui.same_line(position=50)
            _, self.rotation[0] = imgui.input_float('##rotation x', self.rotation[0])
            imgui.text('y:')
            imgui.same_line(position=50)
            _, self.rotation[1] = imgui.input_float('##rotation y', self.rotation[1])
            imgui.text('z:')
            imgui.same_line(position=50)
            _, self.rotation[2] = imgui.input_float('##rotation z', self.rotation[2])
            
            imgui.separator()
            imgui.text('Scale:')
            imgui.text('x:')
            imgui.same_line(position=50)
            _, self.scale[0] = imgui.input_float('##scale x', self.scale[0])
            imgui.text('y:')
            imgui.same_line(position=50)
            _, self.scale[1] = imgui.input_float('##scale y', self.scale[1])
            imgui.text('z:')
            imgui.same_line(position=50)
            _, self.scale[2] = imgui.input_float('##scale z', self.scale[2])
            imgui.end_child()

class CameraSettingsPanel(object):
    def __init__(self):
        self.fov = 0.0
        self.near_plane = 0.0
        self.far_plane = 0.0
        self.CameraFocusRequested = Signal()

    def Update(self):
        """Builds IMGui widgest that make this panel"""
        if imgui.collapsing_header("Camera Settings")[0]:
            imgui.begin_child("#Camera Settings Panel", width=0, height=120, border=True)
            imgui.text('FOV: ')
            imgui.same_line(position=150)
            _, self.fov = imgui.input_float('##fov', self.fov)
            imgui.text('Near Plane: ')
            imgui.same_line(position=150)
            _, self.near_plane = imgui.input_float('##near plane', self.near_plane)
            imgui.text('Far Plane: ')
            imgui.same_line(position=150)
            _, self.far_plane = imgui.input_float('##far plane', self.far_plane)
            if imgui.button('Focus Camera', width=imgui.get_content_region_available_width()):
                self.CameraFocusRequested.send(None)
            imgui.end_child()

class LightSettingsPanel(object):
    def __init__(self):
        self.light_color = [1, 1, 1]
        self.light_intensity = 1.0

    def Update(self) -> None:
        """Builds IMGui widgest that make this panel"""
        if imgui.collapsing_header("Light Settings")[0]:
            imgui.begin_child("##Light Settings Panel", width=0, height=120, border=True)
            imgui.text('Color')
            imgui.same_line(position=150)
            _, self.light_color = imgui.color_edit3('##Light Color', *self.light_color)
            imgui.text('Intensity')
            imgui.same_line(position=150)
            _, self.light_intensity = imgui.slider_float('##Light Intenisty', self.light_intensity, 0.0, 10.0)
            imgui.end_child()

class MaterialSettingsPanel(object):
    def __init__(self):
        self.color = [1.0, 1.0, 1.0]
        self.rougness = 0.0
        self.specular = 1.0
        self.F0 = 0.04

    def Update(self):
        """Builds IMGui widgest that make this panel"""
        if imgui.collapsing_header("Material Settings")[0]:
            imgui.begin_child("##Material Settings Panel", width=0, height=120, border=True)
            imgui.text('Base Color')
            imgui.same_line(position=150)
            _, self.color = imgui.color_edit3('##Base Color', *self.color)
            imgui.text('Rougness')
            imgui.same_line(position=150)
            _, self.rougness = imgui.slider_float('##Roughness', self.rougness, 0.0, 1.0)
            imgui.text('F0')
            imgui.same_line(position=150)
            _, self.F0 = imgui.slider_float('##F0', self.F0, 0.0, 1.0)
            imgui.text('Specular')
            imgui.same_line(position=150)
            _, self.specular = imgui.slider_float('##Specular', self.specular, 0.0, 1.0)
            imgui.end_child()