import os
import easygui
import imgui
from decimal import Decimal, ROUND_DOWN
from imgui.integrations.glfw import GlfwRenderer as IMRenderer
from glfw import _GLFWwindow
from blinker import Signal

class AppGUI(object):
    def __init__(self, win_handle: _GLFWwindow):
        imgui.create_context()
        self.__impl = IMRenderer(win_handle)
        self.import_settings = ImportSettingsPanel()
        self.scene_stats = SceneStatsPanel()
        self.overlays = OverlaysPanel()
        self.camera_settings = CameraSettingsPanel()
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
        self.camera_settings.Update()
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
        if imgui.tree_node('Scene Stats'):
            imgui.text('FPS: ')
            imgui.same_line(position=200)
            imgui.text(str(self.fps))
            imgui.text('Frames: ')
            imgui.same_line(position=200)
            imgui.text(str(self.frames))
            imgui.text('Vertices: ')
            imgui.same_line(position=200)
            imgui.text(str(int(self.num_vertex)))
            imgui.text('Triangles: ')
            imgui.same_line(position=200)
            imgui.text(str(int(self.num_triangles)))
            imgui.text('Min Extends: ')
            imgui.same_line(position=200)
            imgui.text(str(Decimal(self.min_ext[0]).quantize(Decimal('1.00'), ROUND_DOWN)))
            imgui.same_line()
            imgui.text(str(Decimal(self.min_ext[1]).quantize(Decimal('1.00'), ROUND_DOWN)))
            imgui.same_line()
            imgui.text(str(Decimal(self.min_ext[2]).quantize(Decimal('1.00'), ROUND_DOWN)))
            imgui.text('Mix Extends: ')
            imgui.same_line(position=200)
            imgui.text(str(Decimal(self.max_ext[0]).quantize(Decimal('1.00'), ROUND_DOWN)))
            imgui.same_line()
            imgui.text(str(Decimal(self.max_ext[1]).quantize(Decimal('1.00'), ROUND_DOWN)))
            imgui.same_line()
            imgui.text(str(Decimal(self.max_ext[2]).quantize(Decimal('1.00'), ROUND_DOWN)))
            imgui.tree_pop()
        imgui.separator()

class OverlaysPanel(object):
    def __init__(self):
        self.wireframe_only = False
        self.wireframe_shaded = False

    def Update(self) -> None:
        """Builds IMGui widgest that make this panel"""
        if imgui.tree_node('Overlays'):
            imgui.text('Wireframe Shaded:')
            imgui.same_line(position=200)
            _, self.wireframe_shaded = imgui.checkbox('##Wireframe Shaded', self.wireframe_shaded)
            imgui.text('Wireframe Only:')
            imgui.same_line(position=200)
            _, self.wireframe_only = imgui.checkbox('##Wireframe Only', self.wireframe_only)
            imgui.tree_pop()
        imgui.separator()

class ImportSettingsPanel(object):
    def __init__(self):
        self.model_filepath = None
        self.ModelRequestSignal = Signal()
        self.ModelReloadSignal = Signal()

    def Update(self):
        if imgui.tree_node('Import Settings'):
            imgui.text(str(os.path.basename(self.model_filepath)))
            if imgui.button('Load Model'):
                self.model_filepath = easygui.fileopenbox()
                self.ModelRequestSignal.send(self.model_filepath)
            if imgui.button('Reload'):
                self.ModelReloadSignal.send(None)
            imgui.tree_pop()
        imgui.separator()

class TransformsPanel(object):
    def __init__(self):
        self.spin_model = True
        self.translation = [0.0, 0.0, 0.0]
        self.rotation = [0.0, 0.0, 0.0]
        self.scale = [1.0, 1.0, 1.0]

    def Update(self):
        """Builds IMGui widgest that make this panel"""
        if imgui.tree_node('Transform'):
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
            imgui.tree_pop()
        imgui.separator()

class CameraSettingsPanel(object):
    def __init__(self):
        self.fov = 0.0
        self.near_plane = 0.0
        self.far_plane = 0.0
        self.CameraFocusRequested = Signal()

    def Update(self):
        """Builds IMGui widgest that make this panel"""
        if imgui.tree_node('Camera Settings'):
            imgui.text('FOV: ')
            imgui.same_line(position=150)
            _, self.fov = imgui.input_float('##fov', self.fov)
            imgui.text('Near Plane: ')
            imgui.same_line(position=150)
            _, self.near_plane = imgui.input_float('##near plane', self.near_plane)
            imgui.text('Far Plane: ')
            imgui.same_line(position=150)
            _, self.far_plane = imgui.input_float('##far plane', self.far_plane)
            if imgui.button('Focus Camera'):
                self.CameraFocusRequested.send(None)
            imgui.tree_pop()
        imgui.separator()