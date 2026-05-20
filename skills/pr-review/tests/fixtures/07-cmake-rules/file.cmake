cmake_minimum_required(VERSION 3.5)

project(widget)

include_directories(${CMAKE_SOURCE_DIR}/include)
include_directories(/usr/local/include/legacy)

link_directories(/opt/legacy/lib)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -Wall")

file(GLOB SOURCES "src/*.cpp")

add_library(widget ${SOURCES})

target_link_libraries(widget pthread dl)

add_executable(widget_cli main.cpp)
target_link_libraries(widget_cli widget)

if(WIN32)
    add_definitions(-DWIDGET_WINDOWS=1)
endif()
