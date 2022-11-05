cmake_minimum_required(VERSION 3.16)
project(lion_cpp20)

set(CMAKE_CXX_STANDARD 20)

include_directories(/home/tzm/anaconda3/envs/lorraine/include/python3.9)
add_executable(lion_cpp20 main.cpp SCP_Base/SCP.hpp)