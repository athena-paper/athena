#!/usr/bin/env bash
# linking example

if [ "$(uname)" == "Darwin" ]; then
        EXT="dylib"
else
        EXT="so"
fi

cd ../
pwd
make
cd -

LEVEL="../../.."

TCP_FILES="tcp_ipv4.bc tcp_input.bc tcp_output.bc tcp.bc"
UDP_FILES="udp.bc icmp.bc route.bc udp_diag.bc udp_offload.bc udp_tunnel.bc udplite.bc"

rm -f $1
$LEVEL/Release+Asserts/bin/llvm-link $TCP_FILES -o $1
$LEVEL/Release+Asserts/bin/opt -instnamer -mem2reg $1 -o $1
$LEVEL/Release+Asserts/bin/llvm-dis $1 


TIME=$(date +%s)

$LEVEL/Release+Asserts/bin/opt -stats -time-passes \
  -load $LEVEL/projects/poolalloc/Release+Asserts/lib/LLVMDataStructure.$EXT \
  -load $LEVEL/projects/llvm-deps/Release+Asserts/lib/Constraints.$EXT  \
  -load $LEVEL/projects/llvm-deps/Release+Asserts/lib/sourcesinkanalysis.$EXT \
  -load $LEVEL/projects/llvm-deps/Release+Asserts/lib/pointstointerface.$EXT \
  -load $LEVEL/projects/llvm-deps/Release+Asserts/lib/Deps.$EXT  \
  -load $LEVEL/projects/llvm-deps/Release+Asserts/lib/Security.$EXT  \
  -implicit-function -debug-only=taint < $1 2> tmp.dat > /dev/null

TIME=$(echo "$(date +%s) - $TIME" | bc)
printf "Execution time: %d seconds\n" $TIME

python3 constraint_file.py tmp.dat > /dev/null
python3 constraint_graph.py call-stack call-stack.dot -graph 0 > /dev/null
