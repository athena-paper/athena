"""
    Generate information flow graph in .dot format from constraint file.
"""
import re
import sys
import os
import platform

IGNORED = "llvm.dbg.value"


def main():
    """Main function for generation of graph"""

    if len(sys.argv) <= 2:
        print("Usage: constraint_graph.py [con_file] [out_dot] -op [op]")
        print("\t [con_file]: The *.con file for use")
        print("\t [out_dot]: The *.dot file for output")
        print("\t -graph [0-1]: specifying if generating graph, defaults to 0")
        print("\t\t\t0: just dot file")
        print("\t\t\t1: also generating svg image")

    else:
        gen_graph = 0
        for i in range(3, len(sys.argv)):
            if sys.argv[i] == "-graph":
                gen_graph = int(sys.argv[i + 1])

        with open(sys.argv[2], "w") as tmp_file:
            tmp_file.write("digraph {\n")
            with open(sys.argv[1], "r") as file:
                nodes = set()
                edges = set()
                return_block = {}
                block_seq = {}
                for line in file:
                    line = re.split(r"\|+|[\r\n]+", line)
                    if (line[0] == '[UB]' or line[0] == '[TB]'):
                        if len(line) == 4:
                            if line[1] not in return_block:
                                return_block[line[1]] = set()
                            return_block[line[1]].add(line[2])
                        for i in range(2, len(line) - 1):
                            block_seq[line[1] + ': ' + line[i]] = {}

                print(return_block)
                print(block_seq)

                file.seek(0)
                for line in file:
                    line = re.split(r"\|+|[\r\n]+", line)
                    print(line)
                    if line[0] == '[SCG]':
                        if len(line) == 5:
                            bb = line[1]
                        else:
                            bb = line[1] + ": " + line[4]
                        bb_label = '"' + bb + '"'
                        right = '"' + line[3] + ': entry"'
                        ln_num = line[2].split("L")[1]
                        mid = '"' + line[3] + ': call_site' + ln_num + '"'
                        nodes.add(bb_label)
                        nodes.add(mid + ' [color="red"]')
                        nodes.add(right + ' [color="red"]')
                        out = '"' + line[3] + ': out' + '"'
                        nodes.add(out)
                        if line[3] in return_block:
                            for ret in return_block[line[3]]:
                                edges.add('"' + line[3] + ": " + ret +
                                          '" -> ' + out + "\n")
                        else:
                            edges.add(right + ' -> ' + out + "\n")
                        edge_label = '\t[ label = " ' + line[2] + '" ] '
                        edges.add(bb_label + " -> " + mid + edge_label + "\n")
                        edges.add(mid + " -> " + right + "\n")

                        block_seq[bb][ln_num] = line[3]
                        print(block_seq[bb])
                        nodes.add('"' + bb + '_' + str(len(block_seq[bb])) +
                                  '"')
                for bb in block_seq:
                    count = 0
                    for ln in sorted(block_seq[bb].keys()):
                        if count == 0:
                            left = '"' + bb + '"'
                        else:
                            left = '"' + bb + '_' + str(count) + '"'
                        right = '"' + block_seq[bb][
                            ln] + ': call_site' + ln + '"'
                        if count != 0:
                            edges.add(left + ' -> ' + right + '\n')
                        count += 1
                        left = '"' + block_seq[bb][ln] + ': out"'
                        right = '"' + bb + '_' + str(count) + '"'
                        edges.add(left + ' -> ' + right + '\n')

                file.seek(0)
                for line in file:
                    line = re.split(r"\|+|[\r\n]+", line)
                    if line[0] == '[UB]':
                        block = line[1] + ": " + line[2]
                        if len(block_seq[block]) == 0:
                            left = '"' + line[1] + ": " + line[2] + '"'
                        else:
                            left = '"' + line[1] + ": " + line[2] + "_" + str(
                                len(block_seq[block])) + '"'
                        nodes.add(left)
                        if len(line) > 4:
                            for i in range(3, len(line) - 1):
                                right = '"' + line[1] + ": " + line[i] + '"'
                                nodes.add(right)
                                edges.add(left + " -> " + right + "\n")
                    elif line[0] == '[TB]':
                        block = line[1] + ": " + line[2]
                        if len(block_seq[block]) == 0:
                            left = '"' + line[1] + ": " + line[2] + '"'
                        else:
                            left = '"' + line[1] + ": " + line[2] + "_" + str(
                                len(block_seq[block])) + '"'
                        nodes.add(left + ' [color="red"]')
                        if len(line) > 4:
                            for i in range(3, len(line) - 1):
                                right = '"' + line[1] + ": " + line[i] + '"'
                                nodes.add(right)
                                edges.add(left + " -> " + right + "\n")

                for node in nodes:
                    tmp_file.write("\t" + node + "\n")
                for edge in edges:
                    tmp_file.write("\t" + edge)
                file.close()
            tmp_file.write("}")
            tmp_file.close()

        if gen_graph == 1:
            cmd = "dot -Tsvg " + sys.argv[2] + " -o g.svg"
            os.system(cmd)
            if "WSL" in platform.release():
                os.system("wslview g.svg")
            else:
                os.system("open g.svg")


if __name__ == "__main__":
    main()
