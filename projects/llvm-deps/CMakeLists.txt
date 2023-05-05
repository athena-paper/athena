cmake_minimum_required(VERSION 3.3)
project(llvm_deps)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++17")


message(LLVM_BUILD_ROOT="${LLVM_BUILD_ROOT}")


# find_package(LLVM REQUIRED CONFIG)

message(STATUS "Found LLVM ${LLVM_PACKAGE_VERSION}")
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")


include_directories(${LLVM_INCLUDE_DIRS}
                    ${CMAKE_CURRENT_SOURCE_DIR}/include
                    ${CMAKE_CURRENT_BINARY_DIR}/include
                    ${CMAKE_CURRENT_SOURCE_DIR}/../poolalloc/include)

add_definitions(${LLVM_DEFINITIONS})

set(SOURCE_FILES
    include/Constraints/ConstraintKit.h
    include/Constraints/DepsTypes.h
    include/Constraints/RLConsSoln.h
    include/Constraints/RLConstraint.h
    include/Constraints/RLConstraintKit.h
    include/Constraints/RLConstraints.h
    include/Constraints/PartialSolution.h
    include/Constraints/SolverThread.h
    include/CallContext.h
    include/CallSensitiveAnalysisPass.h
    include/FlowRecord.h
    include/FPCache.h
    include/Infoflow.h
    include/InfoflowSignature.h
    include/InterProcAnalysisPass.h
    include/PointsToInterface.h
    include/SignatureLibrary.h
    include/Slice.h
    include/SourceSinkAnalysis.h
    lib/Constraints/RLConsSoln.cpp
    lib/Constraints/RLConstraintKit.cpp
    lib/Constraints/RLConstraints.cpp
    lib/Constraints/MTSolve.cpp
    lib/Constraints/PartialSolution.cpp
    lib/Constraints/Test.cpp
    lib/Deps/CallContext.cpp
    lib/Deps/Infoflow.cpp
    lib/Deps/InfoflowSignature.cpp
    lib/Deps/SignatureLibrary.cpp
    lib/Deps/Slice.cpp
    lib/Deps/StdLibSignatures.cpp
    lib/Deps/StdLibSignatures.h
    lib/PointsToInterface/PointsToInterface.cpp
    lib/SourceSinkAnalysis/SourceSinkAnalysis.cpp)

add_executable(llvm_deps ${SOURCE_FILES})

target_link_libraries(llvm_deps ${llvm_libs})