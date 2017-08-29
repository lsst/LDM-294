#!/usr/bin/env python
# Take list file with parents and make a tex diagram of the product tree.
# Top of the tree will be left of the page ..
# this allows a LONG list of products.
from __future__ import print_function

from treelib import Tree
import argparse

# pt sizes for box + margin + gap between boex
txtheight = 28
leafHeight = 1.26  # cm space per leaf box .. height of page calc
leafWidth = 3.7  # cm space per leaf box .. width of page calc
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
                print(part[0] + " no parent")

    print("{} Product lines".format(count))
    return ptree


def fixTex(text):
    ret = text.replace("_", "\\_")
    ret = ret.replace("/", "/ ")
    return ret


def slice(ptree, outdepth):
    if (ptree.depth() == outdepth):
        return ptree
    # copy the tree but stopping at given depth
    ntree = Tree()
    nodes = ptree.expand_tree()
    for n in nodes:
        # print("Accesing {}".format(n))
        depth = ptree.depth(n)
        prod = ptree[n].data

        #print("outd={od} mydepth={d} Product: {p.id} name: {p.name} parent: {p.parent}".format(od=outdepth, d=depth, p=prod))
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


def outputWBSPKG(fout,prod):
    print("] {", file=fout, end='')
    if WBS == 1 and prod.wbs != "":
        print(r"{{\tiny \color{{black}}{}}} \newline".format(prod.wbs), file=fout)
    print(r"\textbf{" + prod.name + "}\n ", file=fout, end='')
    # print(r"\newline", file=fout)
    print("};", file=fout)
    if PKG == 1 and prod.pkgs != "":
        print(r"\node ({p.id}pkg) "
            "[tbox,below=3mm of {p.id}.north] {{".format(p=prod),
            file=fout, end='')
        print(r"{\tiny \color{black} \begin{verbatim} " +
            prod.pkgs + r" \end{verbatim} }  };",
            file=fout)
    return

def parent(node):
    return node.data.parent
def id(node):
    return node.data.id

def groupByParent(nodes):
    nn = []
    pars = []
    for n in nodes:
	parent = n.data.parent
	if parent not in pars:
            pars.append(parent)
	    for n2 in nodes:
                if (n2.data.parent == parent) :
		   #print (r"Got {n.data.id} par {n.data.parent} looking for {par}".format(n=n2,par=parent))
	           nn.append(n2)
    return nn;

def organiseRow(r, rowMap): #group according to parent in order of prevous row
    prow=rowMap[r-1]
    row = rowMap[r]
    print(r" organise {n} nodes in  Row {r} by {nn} nodes in {r}-1".format(r=r, n=len(row),nn=len(prow)))
    nrow= []
    for p in prow: #scan parents
	parent = p.data.id
	for n2 in row:
           if (n2.data.parent == parent) :
		   print (r"Got {n.data.id} par {n.data.parent} looking for {par}".format(n=n2,par=parent))
	           nrow.append(n2)
    rowMap[r]=nrow
    return

def layoutRows(rowMap, start, end, count, ptree, children ):
    prow=None
    for r in range(start,end,-1): # Printing last row first
	row = rowMap[r]
        count = count + doRow(fout,ptree,children,row,r)
        if (prow):
            print(r"Output  depth={d},   nodes={n} - now lines for prow={pr} nodes".format(d=r, n=len(row), pr=len(prow)))
            for p in prow:
                prod=p.data
                print(r" \draw[pline]   ({p.id}.north) -- ++(0.0,0.5) -| ({p.parent}.south) ; ".format(p=prod),
                     file=fout )
            prow=row
            row=[]
	else:
            prow=row
    return count

def outputLandW(fout,ptree):
    children= dict() # map of most central child to place this node ABOVE it
    rowMap = dict()
    nodes = ptree.expand_tree(mode=Tree.WIDTH) # default mode=DEPTH
    count = 0
    row=[]
    depth=ptree.depth()
    d=0
    pdepth=d
    prow= None
    # first make rows
    for n in nodes:
        prod =ptree[n].data
        d = ptree.depth(prod.id)
        if d != pdepth: # new row
            #print(r" depth={d},   nodes={n}".format(d=pdepth, n=len(row)))
            rowMap[pdepth] = row
            row=[]
            pdepth=d
        row.append(ptree[n])
    #print(r"Out of loop  depth={d},   nodes={n}".format(d=d, n=len(row)))
    rowMap[d] = row # should be root
    # now group the children under parent .. should be done by WIDT FIRST walk fo tree
    # for r in range(2,depth,1): # root is ok and the next row
    #	organiseRow(r,rowMap)
    #now actually make the tex
    # need to  find row with most leaves .. then layout relative to that..
    wideR = depth
    for r in range(depth,-1,-1): # Look at each row
	rowSize = len(rowMap[r])
        if rowSize > len(rowMap[wideR]):
            wideR=r
    print(r"Widest row  depth={d},   nodes={n}".format(d=wideR, n=len(rowMap[wideR])))
    #now lay out row wideR and UP to root
    count = count + layoutRows(rowMap, start, end, count, ptree, children ):
    # and layout the bottom ot the widest row...

    print("{} Product lines in TeX ".format(count))
    return

def doRow(fout,ptree,children,nodes,depth):
#Assuming the nodes are sorted by parent .. putput the groups of siblings and record
# children the middle child of each group
    sdist=15  #mm  sibling group distance for equal distribution
    ccount=0;
    prev = Product("n", "n", "n", "n", "n", "n", "n", "n", "n")
    sibs = []
    child = None
    ncount= len(nodes)
    for n in nodes:
        prod = n.data
        ccount = ccount + 1
	if (prod.id in children):
	   child = children[prod.id]
	else:
           child= None
        if (depth==0):  # root node
           #print(r"depth==0 {p.id}  parent  {p.parent},   child={c}".format(p=prod, c=child))
           print(r"\node ({p.id}) "
               r"[wbbox, above=15mm of {c}]{{\textbf{{{p.name}}}}};".format(p=prod,c=child),
               file=fout)
        else:
           print(r"\node ({p.id}) [pbox,".format(p=prod), file=fout, end='')
           if (child): # easy case - node aboove child
              print("above={d}mm of {c}".format(d=sdist,c=child), file=fout, end='')
           # need to deal with next children
           dist=1 # siblings close then gap
           if ((prev.parent != prod.parent and ccount >1) or (ccount==ncount) ): # not forgetting the last group
              if (ccount==ncount): #we ar eon the last group tha tis the one we do not prev
	        theProd=prod
              else:
		theProd=prev
                dist=sdist
	      sibs = ptree.siblings(theProd.id)
	      sc = len (sibs)
              msib= (int) ((float) (sc) / 2.0 )
              #print(r"prev={prev.id}  theProd={pr.id}  parent  {pr.parent}, sc={sc}  msib={ms}, prod={p.id}"
	#	" count={cc} ncount={nc}".format(prev=prev,pr=theProd,p=prod, ms=msib, sc=sc, cc=ccount, nc =ncount))
              if (msib !=0):
                  children[theProd.parent] = sibs[msib].data.id
                  print(r" parent  {pr.parent} over  prod {p.id}".format(pr=theProd, p=sibs[msib].data))
              else: #only child
                  children[theProd.parent] = theProd.id
                  print(r" Only child or 1 sibling.  parent  {p.parent} over  prod {p.id} nsibs={sc}".format(p=theProd, sc=sc))
              sibs = []
           if (ccount !=1 and not child ): # easy put out to right
              print("right={d}mm of {p.id}".format(d=dist,p=prev), file=fout, end='')
           #   print(r" GOT leaf  {p.id}".format(p=prod))
	   #if (ccount ==1 and not child ): # this will not get a placement but others will be right of it
              #print(r" GOT snowflake first leaf  {p.id}".format(p=prod))
           #print(r"mydepth={md} depth={dp} {p.id} right={d}mm parent={p.parent} prevparent={pr.parent}"
           #         " prev={pr.id}".format(md=ptree.depth(prod.id),dp=depth,p=prod,d=dist, pr=prev))
           outputWBSPKG(fout,prod)
           prev = prod
    return ccount


def outputTexTree(fout, ptree, paperwidth):
    fnodes = []
    nodes = ptree.expand_tree() # default mode=DEPTH
    count = 0
    prev = Product("n", "n", "n", "n", "n", "n", "n", "n", "n")
    nodec =1
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
                print(r"\node ({p.id}) [pbox,".format(p=prod), file=fout, end='')
                if (prev.parent != prod.parent):  # first child to the right if portrait left if landscape
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
                else:
                    # benetih the sibling
                    dist = gap
                    print("below={}pt of {}".format(dist, prev.id), file=fout, end='')
                outputWBSPKG(fout,prod)
                print(r" \draw[pline] ({p.parent}.east) -| ++(0.4,0) |- ({p.id}.west); ".format(p=prod), file=fout)
            prev = prod
    print("{} Product lines in TeX ".format(count))
    return


def doFile(inFile):
    "This processes a csv and produced a tex tree diagram and a tex longtable."
    f = inFile
    nf = "ProductTree.tex"
    if (land):
       nf = "ProductTreeLand.tex"
    nt = "productlist.tex"
    print("Processing {}-> (figure){} and (table){}".format(f, nf, nt))

    with open(f, 'r') as fin:
        ptree = constructTree(fin)
    ntree = ptree
    paperwidth = 0
    height = 0
    if (outdepth <= 100 ):
        ntree = slice(ptree, outdepth)
        if (land!=1):
            paperwidth = 2
            height = -3

    # ptree.show(data_property="name")
    if (land):
        height = height + ntree.depth() * 4  # cm
        paperwidth = (paperwidth + len(ntree.leaves()) * (leafWidth +.1 ))  # cm
        if paperwidth > 500:
             paperwidth=500
    else:
        paperwidth = paperwidth + ntree.depth() * 6.2  # cm
        height = height + len(ntree.leaves()) * leafHeight  # cm

    with open(nf, 'w') as fout:
        header(fout, paperwidth, height)
        if (land):
            outputLandW(fout, ntree)
            #outputTexTreeLand(fout, ntree, paperwidth)
        else:
            outputTexTree(fout, ntree, paperwidth)
        footer(fout)

    with open(nt, 'w') as tout:
        theader(tout)
        outputTexTable(tout, ptree)
        tfooter(tout)

    return
# End DoDir


def theader(tout):
    print("""
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%  Product table generated by {} do not modify.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
""".format(__file__), file=tout)
    print(r"""\tiny
\begin{longtable}{|p{0.10\textwidth}|p{0.12\textwidth}|p{0.26\textwidth}|p{0.11\textwidth}|p{0.11\textwidth}|p{0.20\textwidth}|}\hline
\textbf{WBS} & Product & Description & Manager & Owner & Packages\\ \hline""",
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

    print(r"""\tikzstyle{pline}=[-, thick]
\begin{document}
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
parser.add_argument("--depth", help="make tree pdf stopping at depth ", type=int, default=100)
parser.add_argument("--land", help="make tree pdf landscape rather than portrait default portrait (1 to make landscape)", type=bool, default=0 )
args = parser.parse_args()
outdepth=args.depth
land=args.land
doFile("productlist.csv")
