from setuptools import setup, find_packages


setup(
    name='Pyrousel',
    version='0.0.2',
    packages=find_packages(),
    install_requires=[
        # python-glcontext
        # python-moderngl
        # python-moderngl-window
        # python-glfw
        # python-imgui
        # python-easygui
        # python-blinker
        # python-trimesh
    ],
    entry_points={
        'console_scripts': [
            'pyrousel=pyrousel.app:Run'
        ]
    }
)