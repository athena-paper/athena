#!/usr/bin/env bash
# linking example

if [ "$(uname)" == "Darwin" ]; then
        EXT="dylib"
else
        EXT="so"
fi

LEVEL="../../.."

LINUX_TCP_FILES="tcp_ipv4.bc tcp_input.bc tcp_output.bc tcp.bc"
LINUX_UDP_FILES="udp.bc icmp.bc route.bc udp_diag.bc udp_offload.bc udp_tunnel.bc udplite.bc"
FREEBSD_TCP_FILES="freebsd_tcp.bc"
FREEBSD_UDP_FILES="freebsd_udp.bc"

if [ $1 == "linux_tcp" ]; then
  FILES=$LINUX_TCP_FILES
elif [ $1 == "linux_udp" ]; then
  FILES=$LINUX_UDP_FILES
elif [ $1 == "freebsd_tcp" ]; then
  FILES=$FREEBSD_TCP_FILES
elif [ $1 == "freebsd_udp" ]; then
  FILES=$FREEBSD_UDP_FILES
else
  echo "----------------------- ERROR -----------------------"
  echo "Run the script with ./run.sh [sys_protocol]."
  echo "[sys_protocol] = {linux_tcp, linux_udp, freebsd_tcp, freebsd_udp}."
fi

rm -f test.bc
$LEVEL/Debug+Asserts/bin/llvm-link $FILES -o test.bc
$LEVEL/Debug+Asserts/bin/opt -instnamer -mem2reg test.bc -o test.bc
$LEVEL/Debug+Asserts/bin/llvm-dis test.bc


TIME=$(date +%s)

$LEVEL/Debug+Asserts/bin/opt -stats -time-passes \
  -load $LEVEL/projects/poolalloc/Debug+Asserts/lib/LLVMDataStructure.$EXT \
  -load $LEVEL/projects/llvm-deps/Debug+Asserts/lib/Constraints.$EXT  \
  -load $LEVEL/projects/llvm-deps/Debug+Asserts/lib/sourcesinkanalysis.$EXT \
  -load $LEVEL/projects/llvm-deps/Debug+Asserts/lib/pointstointerface.$EXT \
  -load $LEVEL/projects/llvm-deps/Debug+Asserts/lib/Deps.$EXT  \
  -load $LEVEL/projects/llvm-deps/Debug+Asserts/lib/Security.$EXT  \
  -implicit-function -debug-only=taint < $1 2> tmp.dat > /dev/null

TIME=$(echo "$(date +%s) - $TIME" | bc)
printf "Execution time: %d seconds\n" $TIME

python3 constraint_file.py tmp.dat > /dev/null
python3 constraint_graph.py call-stack ./results/$1.dot -graph 0 > /dev/null

rm -f tmp.dat
rm -f call-stack
