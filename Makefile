export TEXMFHOME = lsst-texmf/texmf

TEX=DDMP.tex	dmgroups.tex	dmroles.tex	leadtutes.tex	probman.tex LDM-294.tex	devprocess.tex	dmorg.tex	dmwbs.tex dmarc.tex	dmproducts.tex	intro.tex 

all : LDM-294.pdf 

LDM-294.pdf: *.tex wbslist.tex
	latexmk -bibtex -pdf -f LDM-294.tex

acronyms.tex:${TEX} myacronyms.tex
	acronyms.csh  ${TEX}

wbslist.tex: wbs/*tex productlist.csv
	python makeWbs.py
