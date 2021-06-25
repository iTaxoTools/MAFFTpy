"""A setuptools based setup module."""

# Always prefer setuptools over distutils
from setuptools import setup, find_namespace_packages, Command, Extension
from setuptools.command.build_ext import build_ext as _build_ext
import pathlib

here = pathlib.Path(__file__).parent.resolve()

class CommandPthread(Command):
    """Custom command for compiling the pthread-win32 library"""
    description = 'compile pthread-win32'
    user_options = []
    def initialize_options(self):
        """virtual overload"""
        pass
    def finalize_options(self):
        """virtual overload"""
        pass
    def run(self):
        """build_pthread"""
        print('PTHREAD COMPILATION PLACEHOLDER for VS cmd: nmake VC-static')

class build_ext(_build_ext):
    """Overrides setuptools build_ext to execute build_init commands"""
    def build_extensions(self):
        for ext in self.extensions:
            if hasattr(ext, 'build_init'):
                ext.build_init(self)
        _build_ext.build_extensions(self)

class MafftExtension(Extension):
    """Extension subclass that defines build_init"""
    def build_init(self, build):
        """Called by build_ext to compile and include pthread-win32 if needed"""
        if build.compiler.compiler_type == 'msvc':
            self.define_macros += [('_CRT_SECURE_NO_WARNINGS', '1')]
            self.include_dirs += ['src/pthread-win32']
            self.library_dirs += ['src/pthread-win32']
            self.libraries += ['libpthreadVC3']
            build.run_command('build_pthread')

mafft_core = 'src/mafft/core'
mafft_module = MafftExtension('itaxotools.mafftpy.mafft',
        include_dirs = [mafft_core],
        define_macros = [
            ('enablemultithread', '1'),
            ('ismodule', '1')
            ],
        library_dirs  = [],
        libraries  = [],
        sources = [
            mafft_core + '/wrapio.c',
            mafft_core + '/mafftmodule.c',
            mafft_core + '/disttbfast.c',
            mafft_core + '/tbfast.c',
            mafft_core + '/dvtditr.c',
            mafft_core + '/mtxutl.c',
            mafft_core + '/mltaln9.c',
            mafft_core + '/defs.c',
            mafft_core + '/io.c',
            mafft_core + '/tddis.c',
            mafft_core + '/constants.c',
            mafft_core + '/Salignmm.c',
            mafft_core + '/Dalignmm.c',
            mafft_core + '/partSalignmm.c',
            mafft_core + '/Lalignmm.c',
            mafft_core + '/rna.c',
            mafft_core + '/Falign.c',
            mafft_core + '/Falign_localhom.c',
            mafft_core + '/Galign11.c',
            mafft_core + '/Lalign11.c',
            mafft_core + '/genalign11.c',
            mafft_core + '/SAalignmm.c',
            mafft_core + '/MSalignmm.c',
            mafft_core + '/fft.c',
            mafft_core + '/fftFunctions.c',
            mafft_core + '/addfunctions.c',
            mafft_core + '/pairlocalalign.c',
            mafft_core + '/MSalign11.c',
            mafft_core + '/nj.c',
            mafft_core + '/tditeration.c',
            mafft_core + '/treeOperation.c',
            ],
        )

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='mafftpy',
    version='0.0.3',
    description='A Python wrapper for MAFFT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Patmanidis Stefanos',
    author_email='stefanpatman91@gmail.com',
    package_dir={'': 'src'},
    packages=find_namespace_packages(
        # exclude=('itaxotools.common*',),
        include=('itaxotools*',),
        where='src',
    ),
    ext_modules = [mafft_module],
    python_requires='>=3.9, <4',
    install_requires=[
        'pyside6',
        ],
    entry_points={
        'console_scripts': [
            'mafftpy = itaxotools.mafftpy.run:main',
            'mafftpy-ginsi = itaxotools.mafftpy.run:ginsi',
            'mafftpy-fftns1 = itaxotools.mafftpy.run:fftns1',
            'mafftpy-qt = itaxotools.mafftpy.gui.run:main',
        ],
        'pyinstaller40': [
          'hook-dirs = itaxotools.__pyinstaller:get_hook_dirs',
          'tests = itaxotools.__pyinstaller:get_PyInstaller_tests'
        ]
    },
    cmdclass = {
        'build_pthread': CommandPthread,
        'build_ext': build_ext,
    },
    classifiers = [
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],
    include_package_data=True,
)
