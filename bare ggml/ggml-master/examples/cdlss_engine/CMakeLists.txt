#
# cdlss_engine
#

set(TEST_TARGET cdlss_engine)

if (BUILD_SHARED_LIBS)
    add_library(${TEST_TARGET} SHARED cdlss_engine.cpp)
else()
    add_executable(${TEST_TARGET} cdlss_engine.cpp)
    set_target_properties(${TEST_TARGET} PROPERTIES ENABLE_EXPORTS TRUE)
endif()

target_link_libraries(${TEST_TARGET} PRIVATE ggml common common-ggml)
