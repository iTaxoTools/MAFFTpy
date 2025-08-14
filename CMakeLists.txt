cmake_minimum_required(VERSION 3.18)
project(${SKBUILD_PROJECT_NAME} LANGUAGES C)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

find_package(Python REQUIRED COMPONENTS Interpreter Development.Module)

set(MAFFT_SRC
    src/mafft/core/wrapio.c
    src/mafft/core/mafftmodule.c
    src/mafft/core/disttbfast.c
    src/mafft/core/tbfast.c
    src/mafft/core/dvtditr.c
    src/mafft/core/mtxutl.c
    src/mafft/core/mltaln9.c
    src/mafft/core/defs.c
    src/mafft/core/io.c
    src/mafft/core/tddis.c
    src/mafft/core/constants.c
    src/mafft/core/Salignmm.c
    src/mafft/core/Dalignmm.c
    src/mafft/core/partSalignmm.c
    src/mafft/core/Lalignmm.c
    src/mafft/core/rna.c
    src/mafft/core/Falign.c
    src/mafft/core/Falign_localhom.c
    src/mafft/core/Galign11.c
    src/mafft/core/Lalign11.c
    src/mafft/core/genalign11.c
    src/mafft/core/SAalignmm.c
    src/mafft/core/MSalignmm.c
    src/mafft/core/fft.c
    src/mafft/core/fftFunctions.c
    src/mafft/core/addfunctions.c
    src/mafft/core/pairlocalalign.c
    src/mafft/core/MSalign11.c
    src/mafft/core/nj.c
    src/mafft/core/tditeration.c
    src/mafft/core/treeOperation.c
    src/mafft/core/makedirectionlist.c
    src/mafft/core/setdirection.c
)

python_add_library(_mafft MODULE ${MAFFT_SRC} WITH_SOABI)

target_compile_definitions(_mafft PRIVATE
    enablemultithread=1
    ismodule=1
)

if(WIN32)

    target_compile_definitions(_mafft PRIVATE
    _CRT_SECURE_NO_WARNINGS=1
    )

    # Add pthreads dependency

    set(PTHREAD_DIR ${PROJECT_SOURCE_DIR}/src/pthread-win32)
    set(PTHREAD_STAMP ${PTHREAD_DIR}/pthreadVC3.inlined_static_stamp)

    add_custom_command(
        OUTPUT ${PTHREAD_STAMP}
        COMMAND nmake VC-static
        WORKING_DIRECTORY ${PTHREAD_DIR}
        COMMENT "Building pthread-win32 static library"
        VERBATIM
    )

    add_custom_target(pthread_win32_lib ALL
        DEPENDS ${PTHREAD_STAMP}
    )

    add_dependencies(_mafft pthread_win32_lib)

    # Include and link pthreads

    target_include_directories(_mafft PRIVATE
        ${PROJECT_SOURCE_DIR}/src/pthread-win32
    )

    target_link_directories(_mafft PRIVATE
        ${PROJECT_SOURCE_DIR}/src/pthread-win32
    )

    target_link_libraries(_mafft PRIVATE libpthreadVC3)
endif()

target_include_directories(_mafft PRIVATE
    ${PROJECT_SOURCE_DIR}/src/mafft/core
    ${Python_INCLUDE_DIRS}
)

install(TARGETS _mafft DESTINATION itaxotools)
