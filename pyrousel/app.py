import argparse
from dataclasses import dataclass
from .appwindow import AppWindow

@dataclass
class ApplicationSettings:
    window_width: int = 1024
    window_height: int = 1024
    startup_model: str = None
    enable_gui: bool = True

def Main() -> None:
    args = ParseArgs()
    if args is None:
        exit(1)
    
    app_settings = ApplicationSettings()
    app_settings.window_width = args.width
    app_settings.window_height = args.height
    app_settings.startup_model = args.model
    app_settings.enable_gui = not args.nogui

    Run(app_settings)
    exit(0)

def Run(settings: ApplicationSettings = ApplicationSettings()) -> None:
    print('Running Pyrousel...')
    print(f'--Window size: {settings.window_width}x{settings.window_height}')
    print(f'--gui: {settings.enable_gui}')
    print(f'--Startup model: {settings.startup_model}')
    print('\n')
    
    app_window = AppWindow(settings.window_width, settings.window_height, settings.enable_gui)
    app_window.Init()

    if settings.startup_model is not None:
        app_window.OnModelRequested(settings.startup_model)
    
    app_window.Run()
    print('Quitting Pyrousel')

def ParseArgs():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '--width',
        type=int,
        default=1024,
        required=False,
        help='window width in pixels'
    )
    arg_parser.add_argument(
        '--height',
        type=int,
        default=1024,
        required=False,
        help='window height in pixels'
    )
    arg_parser.add_argument(
        '--model',
        type=str,
        default=None,
        required=False,
        help='filepath to initial model file'
    )
    arg_parser.add_argument(
        '--nogui',
        action='store_true',
        default=False,
        required=False,
        help='disable interactive property panel'
    )

    args = None
    try:
        args = arg_parser.parse_args()
    except Exception as err:
        err.print()
        arg_parser.print_help()

    return args