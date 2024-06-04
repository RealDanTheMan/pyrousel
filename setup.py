from setuptools import setup, find_packages


setup(
    name='Pyrousel',
    version='0.1.0',
    description='Simple OpenGL based model viewer',
    author='Dan Wulczynski',
    url='https://github.com/RealDanTheMan/pyrousel',
    packages=find_packages(),
    package_data={'pyrousel': ['resources/*']},
    install_requires=[
        "pyopengl",
        "glcontext",
        "moderngl",
        "moderngl-window",
        "glfw",
        "imgui",
        "easygui",
        "blinker"
        "trimesh"
    ],
    entry_points={
        'console_scripts': [
            'pyrousel=pyrousel.app:Run'
        ]
    }
)