from dataclasses import dataclass
from .appwindow import AppWindow

@dataclass
class ApplicationSettings:
    window_width: int = 1024
    window_height: int = 1024

def Run(settings: ApplicationSettings = ApplicationSettings()) -> None:
    print('Running Pyrousel...')
    app_window = AppWindow(settings.window_width, settings.window_height)
    app_window.Init()    
    app_window.Run()
    print('Quitting Pyrousel')

