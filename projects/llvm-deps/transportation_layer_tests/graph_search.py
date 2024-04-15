# -*- coding: utf-8 -*-

import os, sys
from pathlib import Path
basepath = lambda x: './' + x
sink_name = sys.argv[1]
dot_name = sys.argv[2]

import networkx as nx
import re


G = nx.DiGraph(nx.nx_pydot.read_dot(basepath(dot_name)))



# Statistics
print("G has {} nodes and {} edges".format(len(G.nodes), len(G.edges)))
cnt = 0
for node in G.nodes:
    if 'color' in G.nodes[node] and G.out_degree(node) > 1:
        cnt += 1
print("{} tainted branches.".format(cnt))

import logging
from math import log

single_entropy = lambda x: 0 if x == 0 else x*log(1/x, 2)
se = single_entropy
entropy = lambda l: sum([se(i) for i in l])
def entropy_without_nonsink(l):
    p_x = 1 - sum(l)
    return entropy(l + [p_x])
logging.basicConfig(level=logging.WARNING)
#len(list(G.nodes))

def find_filename(func: str):
    '''
    Find the corresponding filename given a function name.
    We look for the function name in the SCG part of tmp.dat.
    '''
    with open(basepath("tmp.dat"), "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith('[SCG]'):
                parts = line.split('|')
                #print(parts[1], func)
                if parts[1] == func :
                    res = parts[2].split(',')
                    return [res[0], res[1].strip()[1:]]
    return None

def find_last_branch_of_bb(func: str, bb: str):
    '''ir_pattern = r'^\s*define\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*)\)\s*(#.*)?\s*[{]'
    start_ln = -1
    with open("test.ll", "r") as f:
        for idx, line in enumerate(f):
            match = re.match(ir_pattern, line)
            if match:
                start_ln = idx
                break
        if start_ln < 0:
            raise IndexError("")
        lines = f.readlines()
        bb_start_ln = -1
        for idx in range(start_ln, len(lines)):
            if lines[idx].startswith(bb):
                bb_start_ln = idx
                break
        if bb_start_ln < 0:
            raise IndexError("")
        bb_end_ln = -1
        for idx in range(bb_start_ln, len(lines)):
            if lines[idx].strip() == "":
    '''
    with open(basepath("test.ll"), "r") as f:
        lines = f.readlines()
        ir_pattern = r'^\s*define\s+.*' + func + '\s*\(.*'
        for idx, line in enumerate(lines):
            if re.match(ir_pattern, line):
                #print(line)
                for j in range(idx+1, len(lines)):
                    if lines[j].startswith(bb):
                        for k in range(j+1, len(lines)):
                            if not lines[k].strip():
                                last_br = lines[k-1]
                                dbg_ln = last_br.split("!")[-1]
                                try:
                                    return int(dbg_ln)
                                except:
                                    return 0                                    
                        return None
                return None
        return None

def split_bb_name(bb):
    if not isinstance(bb, str):
        raise TypeError("")
    i = bb.split(":")
    return i[0].strip(), i[1].strip()

def locate_branch(dbg_ln: int):
    #dbg_pattern = r'^!' + str(dbg_ln) + r'\s*=\s*!MDLocation\(line:\s*(\d+),'
    with open(basepath("test.ll"), "r") as f:
        for line in f:
            if line.startswith("!" + str(dbg_ln)):
                #print(line)
                try:
                    mdloc = line.split("!MDLocation(line:")[1]
                    b_value = mdloc.split(",")[0].strip()
                    return b_value
                except:
                    logging.warning("locate_branch(): Not found!")
                    return None
    return None

def print_detail(branches):
    for branch in branches:
        func, bb = split_bb_name(branch)
        fn = find_filename(func)
        logging.warning(fn)
        ln = locate_branch(find_last_branch_of_bb(func, bb))
        if not fn or not ln:
            pass
        else:
            print("{} / At {}: L{}".format(branch, fn[0], ln))

# Because the graph is NOT a DAG yet, we need to remove all cycles before we can topological sort it.
#all_cycles = list(nx.simple_cycles(G))
n_cycle = 0
while True:
    try:
        cycle = nx.find_cycle(G, orientation='original')
    except nx.exception.NetworkXNoCycle:
        break
    print(n_cycle)
    n_cycle += 1
    # cycle is a list of edges
    #print(cycle)
    try:
        G.remove_edge(cycle[-1][0], cycle[-1][1])
        G.nodes[cycle[-1][0]]['color'] = 'read'
    except:
        pass
        print("Failed to remove edge ({}, {})".format(cycle[-1], cycle[0]))
try:
    logging.warning(nx.find_cycle(G, orientation="original"))
except nx.NetworkXNoCycle:
    logging.debug("No cycle found.")

from copy import deepcopy
H = deepcopy(G)

# Magic
#G = H

rts = list(reversed(list(nx.topological_sort(G))))
#print(rts[:10])

sink_names = [sink_name]
# sink_names = ["tcp_send_ack", "tcp_send_challenge_ack", "tcp_send_dupack"]

for idx, sink_name in enumerate(sink_names):
    all_sinks = []
    for node in G.nodes:
        if node.startswith(sink_name + ": call_site"):
            all_sinks.append(node)
    print("Sink: ")
    print(len(all_sinks), all_sinks)
    
for node_name in rts:
    #print(node_name)
    node = G.nodes[node_name]
    #print("Visited: {}".format(node_name))
    p_name = 'p_' + sink_names[0]
    # We need an ad-hoc fix here for non-excluding sinks
    if node_name == sink_names[0] + ": entry":
        #print("Found sink: {}.".format(sink_name))
        node[p_name] = 1
    # Non-sinks
    else:
        if list(G.successors(node_name)):
            n_children = len(list(G.successors(node_name)))
            # If sensitive
            #if 'color' in G.nodes[node_name]:


            # The wildcard check
            all_wildcard = []

            for child in G.successors(node_name):
                if '*' in G.nodes[child]:
                    all_wildcard.append(True)
            if not all_wildcard:
                all_wildcard = False
            else:
                all_wildcard = all(all_wildcard)
            
            if all_wildcard:
                node['*'] = 1
                node[p_name] = 0           
            else:
                for child in G.successors(node_name):
                    if '*' in G.nodes[child]:
                        # Ignore it, do nothing
                        n_children -= 1
                    else:
                    #print("-- child: {}".format(child))
                    #print(G.nodes[child])
                        node[p_name] = node.get(p_name, 0) + (1/n_children) * G.nodes[child][p_name]
        else:
            #print("-- No child.")
            node[p_name] = 0
        # else:
        #     children = list(G.successors(node_name))
        #     if not children:
        #         pass
        #     else:
        #         extract_e = lambda x: entropy_without_nonsink([G.nodes[x]['p_' + sink_name] for sink_name in sink_names])
        #         worst_child = max(children, key = extract_e)
        #         node['p_tcp_send_ack'] = G.nodes[worst_child]['p_tcp_send_ack']
        #         node['p_tcp_send_delayed_ack'] = G.nodes[worst_child]['p_tcp_send_delayed_ack']

for node_name in rts:
    node = G.nodes[node_name]
    #print([node['p_' + sink_name] for sink_name in sink_names])
    try:
        if '*' in node:
            node['e'] = 0
        else:
            node['e'] = entropy_without_nonsink([node[p_name] for sink_name in sink_names])
    except:
        print(node)
        raise ValueError('')

rts = list(reversed(list(nx.topological_sort(G))))
cnt = 0
for node in rts:
    #print(node)
    if G.nodes[node]['e'] > 0 and G.out_degree(node) > 0:
        print(node, G.nodes[node])
        if 'color' in G.nodes[node]:
            cnt += 1
print("{} tainted branches with non-zero entropy.".format(cnt))
print("-----------------")

cnt = 0
for node_name in rts:
    #print(node_name)
    node = G.nodes[node_name]
    if G.successors(node_name):
        n_children = len(list(G.successors(node_name)))
    deltas = [node['e'] - G.nodes[child]['e'] for child in G.successors(node_name)]
    if not deltas:
        node['d_e'] = 0
    else:
        node['d_e'] = max(deltas)
    if node['d_e'] > 0 and 'color' in G.nodes[node_name] and G.out_degree(node_name) > 0:
        print(node_name, node)
        cnt += 1
print("{} branches have non-zero delta.".format(cnt))

maxima = -1
critical_branch = None
additional_branches = []
for node_name in G.nodes:
    if G.nodes[node_name]['d_e'] > maxima:
        critical_branch = node_name
        additional_branches = []
        maxima = G.nodes[node_name]['d_e']
    elif G.nodes[node_name]['d_e'] == maxima:
        additional_branches.append(node_name)
print(maxima, [(i, G.nodes[i]['e'], G.nodes[i]['d_e']) for i in [critical_branch] + additional_branches])
print_detail([critical_branch] + additional_branches)

# Iteration
fixed_nodes = []
it = 1

while True:
    G, H = H, deepcopy(H)
    fixed_nodes += [critical_branch] + additional_branches
    print("Iteration {}".format(it))
    print("Fixed nodes: ", fixed_nodes)
    it += 1

    # subtree_to_remove = set()
    # for fixed_node in fixed_nodes:
    #     subtree_to_remove = subtree_to_remove.union(nx.descendants(G, fixed_node))
    # print(subtree_to_remove)
    # G.remove_nodes_from(subtree_to_remove)

    # Topological sort AGAIN!
    rts = list(reversed(list(nx.topological_sort(G))))

    for node_name in rts:
        #print(node_name)
        node = G.nodes[node_name]
        #print("Visited: {}".format(node_name))

        # We need an ad-hoc fix here for non-excluding sinks
        if node_name == sink_name[0] + ": entry":
            #print("Found sink: {}.".format(sink_name))
            node[p_name] = 1
        # Non-sinks
        elif node_name in fixed_nodes:
            node[p_name] = 0
            node['*'] = 1
        else:
            if list(G.successors(node_name)):
                n_children = len(list(G.successors(node_name)))
                # If sensitive
                #if 'color' in G.nodes[node_name]:


                # The wildcard check
                all_wildcard = []

                for child in G.successors(node_name):
                    if '*' in G.nodes[child]:
                        all_wildcard.append(True)
                if not all_wildcard:
                    all_wildcard = False
                else:
                    all_wildcard = all(all_wildcard)
                
                if all_wildcard:
                    node['*'] = 1
                    node[p_name] = 0           
                else:
                    for child in G.successors(node_name):
                        if '*' in G.nodes[child]:
                            # Ignore it, do nothing
                            n_children -= 1
                        else:
                        #print("-- child: {}".format(child))
                        #print(G.nodes[child])
                            node[p_name] = node.get(p_name, 0) + (1/n_children) * G.nodes[child][p_name]
            else:
                #print("-- No child.")
                node[p_name] = 0
            # else:
            #     children = list(G.successors(node_name))
            #     if not children:
            #         pass
            #     else:
            #         extract_e = lambda x: entropy_without_nonsink([G.nodes[x]['p_' + sink_name] for sink_name in sink_names])
            #         worst_child = max(children, key = extract_e)
            #         node['p_tcp_send_ack'] = G.nodes[worst_child]['p_tcp_send_ack']
            #         node['p_tcp_send_delayed_ack'] = G.nodes[worst_child]['p_tcp_send_delayed_ack']

    for node_name in rts:
        node = G.nodes[node_name]
        #print([node['p_' + sink_name] for sink_name in sink_names])
        try:
            if '*' in node:
                node['e'] = 0
            else:
                node['e'] = entropy_without_nonsink([node['p_' + sink_name] for sink_name in sink_names])
        except:
            print(node)
            raise ValueError('')

    rts = list(reversed(list(nx.topological_sort(G))))
    cnt = 0
    for node in rts:
        #print(node)
        if G.nodes[node]['e'] > 0 and G.out_degree(node) > 0:
            print(node, G.nodes[node])
            if 'color' in G.nodes[node]:
                cnt += 1
    print("{} tainted branches with non-zero entropy.".format(cnt))
    print("-----------------")


    cnt = 0
    for node_name in rts:
        #print(node_name)
        node = G.nodes[node_name]
        if G.successors(node_name):
            n_children = len(list(G.successors(node_name)))
        deltas = [node['e'] - G.nodes[child]['e'] for child in G.successors(node_name)]
        if not deltas:
            node['d_e'] = 0
        else:
            node['d_e'] = max(deltas)
        if node['d_e'] > 0 and 'color' in G.nodes[node_name]:
            #print(node_name, node['d_e'])
            cnt += 1
    print("{} branches have non-zero delta.".format(cnt))

    maxima = -1
    critical_branch = None
    additional_branches = []
    for node_name in G.nodes:
        if not 'comment' in G.nodes[node_name]:
            continue
        if G.nodes[node_name]['d_e'] > maxima:
            critical_branch = node_name
            additional_branches = []
            maxima = G.nodes[node_name]['d_e']
        elif G.nodes[node_name]['d_e'] == maxima:
            additional_branches.append(node_name)
    print(maxima, [(i, G.nodes[i]) for i in [critical_branch] + additional_branches])

    if maxima == 0 or not ([critical_branch] + additional_branches) or it == 40:
        break

print(len(fixed_nodes), fixed_nodes)
