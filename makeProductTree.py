#python
#Take list file with parents and make a tex diagram of the product tree.
# Top of the tree will be left of the page .. this allow a LONG list of products. 

import os
import fileinput




def doFile(inFile ):
	"This processes a csv and produced a  tex tree diagram."
	count =0
        dcount=0
        parent="";
        sibcount = dict();
        child = dict();
	f=inFile 
	nf = f.replace(".csv",".tex")
	print "Processing " + f  +"-> "+ nf 
	fin = open (f,'r')  	
	fout = open (nf,'w')  	
        header(fout)
	for line in fin :
		if line.startswith(",,,,") or line.startswith("id,Item,"):
			continue
		count= count + 1
		part=line.split(","); #id,prod, parent, descr ..
                if (count==1) : # root node
                    fout.write("\\node ("+part[0]+") [wbbox]{\\textbf{"+part[1]+"}}; \n");
                else:
                    #ind = len(parent) - 1
                    #if ind>=0 and parent[ind]==part[2]:
                    pa=part[2]
                    if pa <> "":
                        fout.write("\\node ("+part[0]+") [pbox,")
                        if (pa in child.keys()) :
                            sibs=child[pa]
                        else:
                            sibs=[];
                        sibs.append(part[0])
                        sibcount[part[0]]=dcount
                        child[pa]=sibs
                        if (len(sibs)==1) : # first child ti the right
                            fout.write("right=15mm of "+pa) 
                            parent=pa;
                        else : # benetih the sibling
                            dcount = dcount +1
                            prev = sibs[len(sibs)-2]
                            if (pa == parent):
                                dist=1
                            else:
                                dist = 13 * (dcount - sibcount[prev] )
                                print part[0] + " Parent:"+pa + " dist "+ str(dist) +" prev:"+prev + " sibcount:"+ str(sibcount[prev ]) + "dcount:"+str(dcount)
                                sibcount[prev] = dcount
                            fout.write("below="+str(dist)+"mm of "+prev) 
                        fout.write("] {\\textbf{"+part[1]+"}}; \n")
                        fout.write(" \draw[pline] ("+pa+".east) -| ++(0.4,0)  |- ("+part[0]+".west);\n ")
                    else:
                        fout.write(part[0]+ " no parent \n");
        footer(fout)
	fout.close()
	fin.close()

	print str(inFile) + " ...." + str(count) + " Product lines \n"
	return;
 # End DoDir



def header(fout):
     fout.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
     fout.write("\n")
     fout.write("%")
     fout.write("\n")
     fout.write("% Document:      DM  product tree")
     fout.write("\n")
     fout.write("%")
     fout.write("\n")
     fout.write("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
     fout.write("\n")

     fout.write("\documentclass{article}")
     fout.write("\n")

     fout.write("\usepackage{times,layouts}")
     fout.write("\n")
     fout.write("\usepackage{tikz,hyperref,amsmath}")
     fout.write("\n")
     fout.write("\usetikzlibrary{positioning,arrows,shapes,decorations.shapes,shapes.arrows}")
     fout.write("\n")
     fout.write("\usetikzlibrary{backgrounds,calc}")
     fout.write("\n")

     fout.write("\usepackage[paperwidth=25cm,paperheight=50cm,")
     fout.write("\n")
     fout.write("left=-2mm,top=3mm,bottom=0mm,right=0mm,")
     fout.write("\n")
     fout.write("noheadfoot,marginparwidth=0pt,includemp=false,")
     fout.write("\n")
     fout.write("textwidth=30cm,textheight=50mm]{geometry}")
     fout.write("\n")


     fout.write("\\newcommand\showpage{%")
     fout.write("\n")
     fout.write("\setlayoutscale{0.5}\setlabelfont{\\tiny}\printheadingsfalse\printparametersfalse")
     fout.write("\n")
     fout.write("\currentpage\pagedesign}")
     fout.write("\n")

     fout.write("\hypersetup{pdftitle={DM organisation }, pdfsubject={Diagram illustrating the")
     fout.write("\n")
     fout.write("products in LSST DM }, pdfauthor={ William O\'Mullane}}")
     fout.write("\n")

     fout.write("\\tikzstyle{wbbox}=[rectangle, rounded corners=3pt, draw=black, top color=blue!50!white, bottom color=white, very thick, minimum height=12mm, inner sep=2pt, text centered, text width=30mm] \n")
     fout.write("\\tikzstyle{pbox}=[rectangle, rounded corners=3pt, draw=black, top color=yellow!50!white, bottom color=white, very thick, minimum height=12mm, inner sep=2pt, text centered, text width=30mm] \n")
     fout.write("\\tikzstyle{pline}=[-, thick]")


     fout.write("\\begin{document}\n")
     fout.write("\\begin{tikzpicture}[node distance=0mm]\n")
     return;

def footer(fout):
     fout.write("\end{tikzpicture}\n")
     fout.write("\end{document}\n")
     return;

### MAIN 
doFile("productlist.csv")
