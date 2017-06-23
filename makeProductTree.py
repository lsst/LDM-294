#!/usr/bin/env python
# Take list file with parents and make a tex diagram of the product tree.
# Top of the tree will be left of the page ..
# this allows a LONG list of products.
from __future__ import print_function

from treelib import Tree
import argparse

# pt sizes for box + margin + gap between boex
txtheight = 28
leafHeight = 1.25  # cm space per leaf box .. height of page calc
sep = 2  # inner sep
gap = 4
WBS = 1  # Put WBS on diagram
PKG = 1  # put packages on diagram
outdepth = 100  # set with --depth if you want a shallower tree


class Product(object):
    def __init__(self, id, name, parent, desc, wbs, manager, owner,
                 kind, pkgs):
        self.id = id
        self.name = name
        self.parent = parent
        self.desc = desc
        self.wbs = wbs
        self.manager = manager
        self.owner = owner
        self.kind = kind
        self.pkgs = pkgs


def constructTree(fin):
    "Read the tree file and ocntrcut a tree structure"
    count = 0
    ptree = Tree()
    for line in fin:
        if line.startswith(",,,,") or line.startswith("id,Item,"):
                continue
        count = count + 1
        line = line.replace("\"", "")
        line = line.rstrip('\r\n')
        part = line.split(",")  # id,prod, parent, descr ..

        prod = Product(part[0], part[1], part[2], part[3], part[4], part[6],
                       part[7], part[8], part[9])
        # print("Product:" + prod.id + " name:" + prod.name + " parent:"
        #       + prod.parent)
        if (count == 1):  # root node
            ptree.create_node(prod.id, prod.id, data=prod)
        else:
            # print("Creating node:" + prod.id + " name:"+ prod.name +
            #       " parent:" + prod.parent)
            if prod.parent != "":
                ptree.create_node(prod.id, prod.id, data=prod,
                                  parent=prod.parent)
            else:
                fout.write(part[0] + " no parent \n")

    print("{} Product lines".format(count))
    return ptree


def fixTex(text):
    ret = text.replace("_", "\\_")
    ret = ret.replace("/", "/ ")
    return ret


def slice(ptree, outdepth):
    # copy the tree but stopping at given depth
    ntree = Tree()
    nodes = ptree.expand_tree()
    for n in nodes:
        # print("Accesing {}".format(n))
        depth = ptree.depth(n)
        prod = ptree[n].data

        # print("{} Product: {} name: {} parent: {}".format(depth, prod.id,
        #                                                   prod.name,
        #                                                   prod.parent))
        if (depth <= outdepth):
            # print(" YES ", end='')
            if (prod.parent == ""):
                ntree.create_node(prod.id, prod.id, data=prod)
            else:
                ntree.create_node(prod.id, prod.id, data=prod,
                                  parent=prod.parent)
        # print()
    return ntree


def outputTexTable(tout, ptree):
    nodes = ptree.expand_tree()
    for n in nodes:
        prod = ptree[n].data
        print(r"{p.wbs} &  {p.name} & {p.desc} & {p.manager} & {p.owner} "
              r"& {}\\ \hline".format(fixTex(prod.pkgs), p=prod), file=tout)
    return


def outputTexTree(fout, ptree):
    fnodes = []
    nodes = ptree.expand_tree()
    count = 0
    prev = Product("n", "n", "n", "n", "n", "n", "n", "n", "n")
    # Text height + the gap added to each one
    blocksize = txtheight + gap + sep
    for n in nodes:
        prod = ptree[n].data
        fnodes.append(prod)
        depth = ptree.depth(n)
        count = count + 1
        # print("{} Product: {p.id} name: {p.name}"
        #       " parent: {p.parent}".format(depth, p=prod))
        if (depth <= outdepth):
            if (count == 1):  # root node
                print(r"\node ({p.id}) "
                      r"[wbbox]{{\textbf{{{p.name}}}}};".format(p=prod),
                      file=fout)
            else:
                print(r"\node ({p.id}) [pbox,".format(p=prod),
                      file=fout, end='')
                if (prev.parent != prod.parent):  # first child to the right
                    found = 0
                    scount = count - 1
                    while found == 0 and scount > 0:
                        scount = scount - 1
                        found = fnodes[scount].parent == prod.parent
                    if scount <= 0:  # first sib can go righ of parent
                        print("right=15mm of {p.parent}".format(p=prod),
                              file=fout, end='')
                    else:  # Figure how low to go  - find my prior sibling
                        psib = fnodes[scount]
                        leaves = ptree.leaves(psib.id)
                        depth = len(leaves)
                        lleaf = leaves[depth-1].data
                        # print("Prev: {} psib: {} "
                        #       "llead.parent: {}".format(prev.id, psib.id,
                        #                                 lleaf.parent))
                        if (lleaf.parent == psib.id):
                            depth = depth - 1
                        # if (prod.id=="L2"):
                        #     depth=depth + 1 # Not sure why this is one short
                        # the number of leaves below my sibling
                        dist = depth * blocksize
                        # print("{p.id} Depth: {} dist: {} blocksize: {}"
                        #       " siblin: {s.id}".format(depth, dist,
                        #                                s=psib, p=prod))
                        print("below={}pt of {}".format(dist, psib.id),
                              file=fout, end='')
                else:  # benetih the sibling
                    dist = gap
                    print("below={}pt of {}".format(dist, prev.id),
                          file=fout, end='')
                print("] {", file=fout, end='')
                if WBS == 1 and prod.wbs != "":
                    print(r"{{\tiny \color{{gray}}{}}}"
                          r" \newline".format(prod.wbs), file=fout)
                print(r"\textbf{" + prod.name + "}\n ", file=fout, end='')
                # print(r"\newline", file=fout)
                print("};", file=fout)
                if PKG == 1 and prod.pkgs != "":
                    print(r"\node ({p.id}pkg) "
                          "[tbox,below=3mm of {p.id}.north] {{".format(p=prod),
                          file=fout, end='')
                    print(r"{\tiny \color{gray} \begin{verbatim} " +
                          prod.pkgs + r" \end{verbatim} }  };",
                          file=fout)
                print(r" \draw[pline] ({p.parent}.east) -| ++(0.4,0)  "
                      "|- ({p.id}.west);\n ".format(p=prod),
                      file=fout, end='')
            prev = prod
    print("{} Product lines in TeX ".format(count))
    return


def doFile(inFile):
    "This processes a csv and produced a tex tree diagram and a tex longtable."
    f = inFile
    nf = "ProductTree.tex"
    nt = "productlist.tex"
    print("Processing {}-> (figure){} and (table){}".format(f, nf, nt))

    with open(f, 'r') as fin:
        ptree = constructTree(fin)
    ntree = ptree
    width = 0
    height = 0
    if (outdepth <= 100):
        ntree = slice(ptree, outdepth)
        width = 2
        height = -6

    # ptree.show(data_property="name")

    width = width + ntree.depth() * 6.2  # cm
    height = height + len(ntree.leaves()) * leafHeight  # cm

    with open(nf, 'w') as fout:
        header(fout, width, height)
        outputTexTree(fout, ntree)
        footer(fout)

    with open(nt, 'w') as tout:
        theader(tout)
        outputTexTable(tout, ptree)
        tfooter(tout)

    return
# End DoDir


def theader(tout):
    print("""%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%  Product table generated by {} do not modify.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%""".format(__file__), file=tout)
    print(r"""\tiny
\begin{longtable}{|p{0.08\textwidth}|p{0.17\textwidth}|p{0.26\textwidth}|p{0.12\textwidth}|p{0.12\textwidth}|p{0.22\textwidth}|}\hline
 \bf WBS & Product & Description & Manager & Owner & Packages\\ \hline""",
          file=tout)

    return


def header(fout, pwidth, pheight):
    print(r"""%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
% Document:      DM  product tree
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\documentclass{article}
\usepackage{times,layouts}
\usepackage{tikz,hyperref,amsmath}
\usetikzlibrary{positioning,arrows,shapes,decorations.shapes,shapes.arrows}
\usetikzlibrary{backgrounds,calc}""", file=fout)
    print(r"\usepackage[paperwidth={}cm,paperheight={}cm,".format(pwidth,
          pheight), file=fout)
    print(r"""left=-2mm,top=3mm,bottom=0mm,right=0mm,
noheadfoot,marginparwidth=0pt,includemp=false,
textwidth=30cm,textheight=50mm]{geometry}
\newcommand\showpage{%
\setlayoutscale{0.5}\setlabelfont{\tiny}\printheadingsfalse\printparametersfalse
\currentpage\pagedesign}
\hypersetup{pdftitle={DM products }, pdfsubject={Diagram illustrating the
products in LSST DM }, pdfauthor={ William O'Mullane}}
\tikzstyle{tbox}=[rectangle,text centered, text width=30mm]
\tikzstyle{wbbox}=[rectangle, rounded corners=3pt, draw=black, top color=blue!50!white, bottom color=white, very thick, minimum height=12mm, inner sep=2pt, text centered, text width=30mm]""", file=fout)

    print(r"\tikzstyle{pbox}=[rectangle, rounded corners=3pt, draw=black, top"
          " color=yellow!50!white, bottom color=white, very thick,"
          " minimum height=" + str(txtheight) + "pt, inner sep=" + str(sep) +
          "pt, text centered, text width=35mm]", file=fout)

    print(r"""\tikzstyle{pline}=[-, thick]\begin{document}
\begin{tikzpicture}[node distance=0mm]""", file=fout)

    return


def footer(fout):
    print(r"""\end{tikzpicture}
\end{document}""", file=fout)
    return


def tfooter(tout):
    print(r"""\end{longtable}
\normalsize""", file=tout)
    return


# MAIN

parser = argparse.ArgumentParser()
parser.add_argument("--depth", help="make tree pdf stopping at depth ",
                    type=int)
args = parser.parse_args()
if args.depth is not None:
    outdepth = args.depth
doFile("productlist.csv")
