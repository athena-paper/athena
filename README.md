# Athena: Analyzing and Quantifying Side-Channels of Transport Layer Protocols


- [Athena: Analyzing and Quantifying Side-Channels of Transport Layer Protocols](#athena-analyzing-and-quantifying-side-channels-of-transport-layer-protocols)
  - [Intro](#intro)
  - [System Requirements](#system-requirements)
  - [Building the toolchain](#building-the-toolchain)
  - [Download and compile Linux kernel code](#download-and-compile-linux-kernel-code)
  - [Running the static taint analysis](#running-the-static-taint-analysis)
    - [Configuring the benchmark](#configuring-the-benchmark)
  - [Running the leakage analyzer and mitigator and the rule-based classifier](#running-the-leakage-analyzer-and-mitigator-and-the-rule-based-classifier)
  - [Understanding the final output](#understanding-the-final-output)


## Intro

This is the benchmark repo for the peer-reviewed submission of the paper. The repo has been anonymized for review purposes. A walkthrough of how to use the benchmark and reproduce the results in the paper will be provided in the following sections. 

## System Requirements

We've been building the system under Ubuntu 18.04, which provides the best compatibility of softwares used and convenience in compiling the version of Linux we are analyzing. The instructions in this documentation assumes the user is running this version of Ubuntu Linux.

## Building the toolchain

1. Before building, make sure to check:

- The system's default 'python' is linked to a python2 executable. Check by `python --version`.
- gcc-5 is installed for compiling the LLVM 3.7.1 version. Use `gcc -v` to check version. 
- Use `update-alternatives` to change default `python` and `gcc` of the system if versions does not match.

2. Clone the project. 

3. To build the toolchain, run the commands below.

```sh
# First direct to project's root dir
cd /PATH_TO_LLVM_DIR

# Configure the project under root
./configure

# Run 'make' to build LLVM
make

# Direct to projects folders, configure and make for each package.
cd projects/poolalloc/
./configure
make

cd ../llvm-deps/
./configure
make
```

## Download and compile Linux kernel code

We analyzed Linux kernel v3.19 and v4.8. Here is an example of compiling the Linux v3.19 network IPv4 package.

```sh
# Go to the directory to store 
cd /LINUX_PARENT_DIR

# Download and extract the kernel archive
wget https://cdn.kernel.org/pub/linux/kernel/v3.x/linux-3.19.tar.gz
tar zxvf linux-3.19.tar.gz

# Direct into the Linux folder
cd linux-3.19

# Configure
make allyesconfig
make prepare
make modules_prepare

# Compile
make V=0 \
    CLANG_FLAGS="-emit-llvm-bc" \
    HOSTCC="/PATH_TO_LLVM_DIR/Debug+Asserts/bin/clang --save-temps=obj -no-integrated-as -g" \
    CC="/PATH_TO_LLVM_DIR/Debug+Asserts/bin/clang --save-temps=obj -no-integrated-as -g" \
    -j4 M=net/ipv4 \
    2>/dev/null
```




## Running the static taint analysis

```sh
# Direct to the benchmark folder
cd /PATH_TO_LLVM_DIR/projects/llvm-deps/transportation_layer_tests

# Copy the compiled LLVM bitcode
cp /LINUX_PARENT_DIR/linux-3.19/net/ipv4/*.bc ./
```

### Configuring the benchmark

Before running, you can modify the configuration file, `config.log`. A sample configuration looks like below.

```json
{
  "signature_mode": {
    "direction": 1,
    "pointer": 0,
    "custom": []
  },
  "lattice": {
    "levels": [
      {
        "name": "secret",
        "level": ["public", "private"]
      }
    ],
    "compartments": []
  },
  "source": [
    {
      "function": "tcp_v4_rcv",
      "type": "variable",
      "name": "sk",
      "index": -1,
      "l": {
        "secret": "private"
      },
      "c": {}
    }
  ],
  "sink": [],
  "using_whitelist": true,
  "whitelist": [],
  "entry": ["tcp_v4_rcv"]
}
```

The field to be configured is `entry`, `source`. For TCP, the entry is `tcp_v4_rcv`. For UDP, the entry is one of the two functions `udp_rcv` and `udp_err`. For sources, replace `source` json snippet below for each protocol.

```
# TCP source
  "source": [
    {
      "function": "tcp_v4_rcv",
      "type": "variable",
      "name": "sk",
      "index": -1,
      "l": {
        "secret": "private"
      },
      "c": {}
    }
  ],

# UDP source
  "source": [
    {
      "type": "variable",
      "name": "udp_table",
      "index": -1,
      "l": {
        "secret": "private"
      },
      "c": {}
    }
  ],
```


After done with the configuration file, you can then run the analysis with the prepared script.
```
# Run the analysis
./run.sh test.sh
```

## Running the leakage analyzer and mitigator and the rule-based classifier

```sh
# Under the same directory, run the script with Python 3.x
# Example: python graph_search.py icmp_send udp_rcv.dot
python3 graph_search.py [SINK_NAME] [DOT_NAME]
```

## Understanding the final output

The output of the script is a list of top-ranked branches in the format of their corresponding basic block names. More information (e.g., iteration, number of tainted/critical branches, detailed values of nodes) can also be found in the log printed.

Sample output (simplified):
```
G has 6441 nodes and 7917 edges
526 tainted branches. // Statistical information

['call_rcu_sched: entry', 'call_rcu_sched: call_site562', 'rt_free: bb', 'rt_free: entry', 'rt_free: call_site579', 'fnhe_flush_routes: if.end.39', 'fnhe_flush_routes: do.end.38', 'fnhe_flush_routes: do.cond.37', 'fnhe_flush_routes: do.body.35', 'fnhe_flush_routes: if.then.34'] // The first 10 nodes in reversed topological sort; if this is printed means the cycle removing algorithm succeeds
Sink:
1 ['icmp_send: call_site1954'] // All call sites to nodes


Iteration 1
Fixed nodes:  ['__udp4_lib_rcv: if.end.89']
0 tainted branches with non-zero entropy.
-----------------
1 ['__udp4_lib_rcv: if.end.89'] // Sample output which terminates at the 1st iteration
```







