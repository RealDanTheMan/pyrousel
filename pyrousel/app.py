from pyrousel.appwindow import AppWindow

def Run() -> None:
    print('Running Pyrousel...')
    app_window = AppWindow(1280, 1280)
    app_window.Init()
    app_window.Run()
    print('Quitting Pyrousel')

