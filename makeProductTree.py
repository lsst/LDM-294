#!/usr/bin/env python
# Take list file with parents and make a tex diagram of the product tree.
# Top of the tree will be left of the page ..
# this allows a LONG list of products.
from __future__ import print_function

from treelib import Tree
import argparse
import csv
import re

# pt sizes for box + margin + gap between boex
txtheight = 35
leafHeight = 1.56  # cm space per leaf box .. height of page calc
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
    "Read the tree file and construct  a tree structure"
    count = 0
    ptree = Tree()
    reader= csv.reader(fin,dialect='excel')
    for line in reader:
        count = count + 1
        if count == 1:
            continue
        part = line
        id = fixIdTex(part[1]) #make an id from the name
        pid= fixIdTex(part[3]) #use the same formaula on the parent name then we are good
        name= fixTex(part[2])
        prod = Product(id, name, pid, "", part[4], part[6],
                       part[7], "", part[8])
       # print("Product:" + prod.id + " name:" + prod.name + " parent:" + prod.parent)
        if (count == 2):  # root node
            ptree.create_node(prod.id, prod.id, data=prod)
        else:
            #print("Creating node:" + prod.id + " name:"+ prod.name +
            #      " parent:" + prod.parent)
            if prod.parent != "":
                ptree.create_node(prod.id, prod.id, data=prod,
                                  parent=prod.parent)
            else:
                print(part[0] + " no parent")

    print("{} Product lines".format(count))
    return ptree


def fixIdTex(text):
    id= re.sub(r"\s+","", text)
    id= id.replace("(","")
    id= id.replace(")","")
    id= id.replace("\"","")
    id= id.replace("_", "")
    id= id.replace(".","")
    id= id.replace("&","")

    return id

def fixTex(text):
    ret = text.replace("_", "\\_")
    ret = ret.replace("/", "/ ")
    ret = ret.replace("&", "\\& ")
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
        if prod.wbs:
            print(r"{p.wbs} &  {p.name} & {p.manager} & {p.owner} "
                  r"& {}\\ \hline".format(fixTex(prod.pkgs), p=prod), file=tout)
        else:
            print(r"\multicolumn{{2}}{{l}}{{\textbf{{{p.name}}}}} & {p.manager} & {p.owner} & \\ "
                  r"\hline".format(p=prod), file=tout)
    return


def outputWBSPKG(fout,prod):
    print("] {", file=fout, end='')
    #if WBS == 1 and prod.wbs != "":
        #print(r"{{\small \color{{blue}}{}}} \newline".format(prod.wbs), file=fout)
    print(r"\textbf{" + prod.name + "} ", file=fout, end='')
    print("};", file=fout)
    if WBS == 1 and prod.wbs != "":
        print(r"\node [below right] at ({p.id}.north west) {{\small \color{{blue}}{p.wbs}}} ;".format(p=prod), file=fout)
    if PKG == 1 and prod.pkgs != "":
        print(r"\node ({p.id}pkg) "
            "[tbox,below=3mm of {p.id}.north] {{".format(p=prod),
            file=fout, end='')
        print(r"{\small \color{black} \begin{verbatim} " +
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

def drawLines(fout,row):
    print(r"   nodes={n} - now lines for row={n} nodes  ".format( n=len(row)))
    for p in row:
        prod=p.data
        print(r" \draw[pline]   ({p.id}.north) -- ++(0.0,0.5) -| ({p.parent}.south) ; ".format(p=prod),
             file=fout )
    return

def layoutRows(fout, rowMap, start, end, count, ptree, children,childcount, goingDown ):
    prow=None
    inc = -1
    if goingDown==1:
        inc=+1
    for r in range(start,end,inc): # Printing last row first
        row = rowMap[r]
        count = count + doRow(fout,ptree,children,row,r,childcount, goingDown)
        print(r"Output  depth={d},   nodes={n} start={s} end={e} goingDown={a}".format(d=r, n=len(row), s=start, e=end, a=goingDown))
        if (goingDown==1): #draw lines between current row and parents
            drawLines(fout,row)
        if (prow and goingDown == 0):
           # print(r"Output  depth={d},   nodes={n} - now lines for prow={pr} nodes".format(d=r, n=len(row), pr=len(prow)))
            drawLines(fout,prow)
            prow=row
            row=[]
        else:
            prow=row
    return count

def outputLandMix(fout,ptree):
# attempt to put DM on top of page then each of the top level sub trees in portrait beneath it accross the page ..
    stub = slice(ptree, 1)
    nodes = stub.expand_tree(mode=Tree.WIDTH) # default mode=DEPTH
    row = []
    count =0
    root= None
    child = None
    for n in nodes:
        count= count +1
        if (count ==1): #  root node
           root=ptree[n].data
        else:
           row.append(ptree[n])

    child = row[count//2].data
    sib=None
    count =1 # will output root after
    prev= None
    for n in row: # for each top level element put it out in portrait
        p = n.data
        stree = ptree.subtree(p.id)
        d = 1
        if (prev):
           d = prev.depth()
        if (d==0): d=1
        width =  d  * 6.2  # cm
        print(r" {p.id} {p.parent} depth={d} width={w} ".format(p=p, d=d,w=width ))
        count = count + outputTexTreeP(fout, stree, width, sib, 0)
        sib=p
        prev = stree

    ### place root node
    print(r"\node ({p.id}) "
         r"[wbbox, above=15mm of {c.id}]{{\textbf{{{p.name}}}}};".format(p=root,c=child),
         file=fout)
    drawLines(fout,row)
    print("{} Product lines in TeX ".format(count))
    return

def outputLandW(fout,ptree):
    childcount = dict() # map of counts of children
    children= dict() # map of most central child to place this node ABOVE it
    rowMap = dict()
    nodes = ptree.expand_tree(mode=Tree.WIDTH) # default mode=DEPTH
    count = 0
    row=[]
    depth=ptree.depth()
    d=0
    pdepth=d
    prow= None
    pn= None
    cc =0
    # first make rows
    for n in nodes:
        count= count +1
        prod =ptree[n].data
        if (not pn):
            pn=prod
        d = ptree.depth(prod.id)
        # count the children as well
        if ( not pn.parent == prod.parent):
            childcount[pn.parent]=cc
            print(r" Set {p.parent} : {cc} children".format(p=pn, cc=cc ))
            cc=0
        cc= cc+1
        if d != pdepth: # new row
            #print(r" depth={d},   nodes={n}".format(d=pdepth, n=len(row)))
            rowMap[pdepth] = row
            row=[]
            pdepth=d
            pn= None
        row.append(ptree[n])
        pn = prod
    rowMap[d] = row # should be root
    childcount[pn.parent]=cc
    print(r"Out of loop  depth={d}, rows={r}  nodes={n}".format(d=depth, r=len(rowMap), n=count))
    count=0
    # now group the children under parent .. should be done by WIDT FIRST walk fo tree
    # for r in range(2,depth,1): # root is ok and the next row
    #   organiseRow(r,rowMap)
    #now actually make the tex
    # need to  find row with most leaves .. then layout relative to that..
    wideR = depth
    for r in range(depth,-1,-1): # Look at each row
        rowSize = len(rowMap[r])
        if rowSize > len(rowMap[wideR]):
            wideR=r
    print(r"Widest row  depth={d},   nodes={n} layout {d} to  -1".format(d=wideR, n=len(rowMap[wideR])))
    #now lay out row wideR and UP to root last 0 indicated goingUpward
    count = count + layoutRows(fout,rowMap, wideR, -1, count, ptree, children, childcount, 0 )
    if (wideR != depth):
        print(r"Layout remainder down wideR={w} depth={d}".format(w=wideR+1, d=depth))
        # and layout the the widest row to the bottowm downward ,.
        count = count + layoutRows(fout,rowMap, wideR+1, depth+1, count, ptree, children,childcount,1 )

    print("{} Product lines in TeX ".format(count))
    return

def doRow(fout,ptree,children,nodes,depth, childcount, goingDown):
#Assuming the nodes are sorted by parent .. putput the groups of siblings and record
# children the middle child of each group
# this is for landscaepe outout but gets too wide wut full tree
    sdist=15  #mm  sibling group distance for equal distribution
    ccount=0;
    prev = Product("n", "n", "n", "n", "n", "n", "n", "n", "n")
    sibs = []
    child = None
    ncount= len(nodes)
    pushd=0
    for n in nodes:
        placed=0
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
           placed=1
        else:
           print(r"\node ({p.id}) [pbox,".format(p=prod), file=fout, end='')
           if child and goingDown==0: # easy case - node aboove child
              print("above={d}mm of {c}".format(d=sdist,c=child), file=fout, end='')
              placed=1
           if goingDown==1  and not prev.parent == prod.parent:
              if not ccount==1: # if its the first one just put it left
                 ddist=sdist
                 if childcount[prod.parent] > 4 : # I got siblings
                     if pushd==0:
                         pushd=1
                         ddist= 3* sdist
                     else:
                         pushd=0
                 print("below={d}mm of {p.parent}".format(d=ddist,p=prod), file=fout, end='')
              placed=1
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
        #       " count={cc} ncount={nc}".format(prev=prev,pr=theProd,p=prod, ms=msib, sc=sc, cc=ccount, nc =ncount))
              if (msib !=0):
                  children[theProd.parent] = sibs[msib].data.id
                  #print(r" parent  {pr.parent} over  prod {p.id}".format(pr=theProd, p=sibs[msib].data))
              else: #only child
                  children[theProd.parent] = theProd.id
                  #print(r" Only child or 1 sibling.  parent  {p.parent} over  prod {p.id} nsibs={sc}".format(p=theProd, sc=sc))
              sibs = []
           if (not ccount==1 and not child  and goingDown==0 or (goingDown ==1 and placed==0 )): # easy put out to right
                # distance should account for how many children lie beneath the sibling to the left
              if prev and prev.id in childcount:
                 dist = childcount[prev.id] * 15  + 1
                 #print(r" dist  {d} prev {p.id} {nc} children".format(p=prev, d=dist, nc=childcount[prev.id]))
              print("right={d}mm of {p.id}".format(d=dist,p=prev), file=fout, end='')
              placed=1
           #print(r"mydepth={md} depth={dp} {p.id} right={d}mm parent={p.parent} prevparent={pr.parent}"
           #         " prev={pr.id}".format(md=ptree.depth(prod.id),dp=depth,p=prod,d=dist, pr=prev))
           outputWBSPKG(fout,prod)
           prev = prod
    return ccount


def outputTexTree(fout, ptree, paperwidth):
    count = outputTexTreeP(fout, ptree, paperwidth, None, 1)
    print("{} Product lines in TeX ".format(count))
    return

def outputTexTreeP(fout, ptree, width, sib, full):
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
            if (count == 1 ):  # root node
                if full ==1:
                   print(r"\node ({p.id}) "
                      r"[wbbox]{{\textbf{{{p.name}}}}};".format(p=prod),
                      file=fout)
                else: #some sub tree
                   print(r"\node ({p.id}) [pbox, ".format(p=prod), file=fout)
                   if (sib):
                      print("right={d}cm of {p.id}".format(d=width,p=sib), file=fout, end='')
                   outputWBSPKG(fout,prod)

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
    return count


def mixTreeDim(ptree):
    "Return the max second level nodes is counting how many leaves."
    n2l = 0
    nmaxSub = 0
    nodes = ptree.expand_tree()
    for n in nodes:
        depth = ptree.depth(n)
        #print(depth)
        if depth == 1:
            n2l = n2l +1
            #print('> leaves:', len(ptree.leaves(n)))
            subL = len(ptree.leaves(n))
            if subL > nmaxSub:
               nmaxSub = subL
    return (n2l, nmaxSub)

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

    n2, nMS = mixTreeDim(ptree)    

    print('>n2 - tree depth: ', n2, ntree.depth(), nMS)

    paperwidth = 0
    height = 0
    if (outdepth <= 100 ):
        ntree = slice(ptree, outdepth)
        if (land!=1):
            paperwidth = 2
            height = -3

    # ptree.show(data_property="name")
    #if (land==1):   #full landscape
    #  paperwidth = paperwidth + len(ntree.leaves()) * 6.2 # cm
    #  height = height + ntree.depth() * leafHeight + 0.5  # cm
    #elif (land==2):  #mixed landscape/portrait
    if (land):
      paperwidth = paperwidth + ( ntree.depth() * 5.2 ) * n2 + 0.7 # cm
      streew=paperwidth
      height = height + nMS * 1.6  # cm
      print('height:', height, 'width:', paperwidth)
    else:
      paperwidth = paperwidth + ntree.depth() * 6.2  # cm
      streew=paperwidth
      height = height + len(ntree.leaves()) * leafHeight + 0.5 # cm

    with open(nf, 'w') as fout:
        header(fout, paperwidth, height)
        if (land):
            #outputLandW(fout, ntree)
            outputLandMix(fout, ntree)
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
    print(r"""\scriptsize
\begin{longtable}{
p{0.15\textwidth}   |p{0.15\textwidth}|p{0.15\textwidth} |p{0.22\textwidth}|p{0.19\textwidth}}
\multicolumn{1}{c|}{\textbf{WBS Element}} &
\multicolumn{1}{c|}{\textbf{Product}} &
\multicolumn{1}{c|}{\textbf{Manager}} &
\multicolumn{1}{c|}{\textbf{Owner}} &
\multicolumn{1}{c}{\textbf{Packages}}\\ \hline""",
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
parser.add_argument("--file", help="Input csv file ", default='DM Product Properties.csv')
args = parser.parse_args()
outdepth=args.depth
land=args.land
inp=args.file
doFile(inp)
