export TEXMFHOME = lsst-texmf/texmf

TEX=DDMP.tex	dmgroups.tex	dmroles.tex	leadtutes.tex	probman.tex LDM-294.tex	devprocess.tex	dmorg.tex	dmwbs.tex dmarc.tex	dmproducts.tex	intro.tex  

all : LDM-294.pdf

LDM-294.pdf: *.tex wbslist.tex ProductTree.pdf ProductTreeLand.pdf
	latexmk -bibtex -pdf -f LDM-294.tex

acronyms:${TEX} myacronyms.tex
	acronyms.csh  ${TEX}

wbslist.tex: wbs/*tex productlist.csv
	python makeWbs.py

ProductTree.tex: productlist.csv
	python --version
	python makeProductTree.py --depth=2

ProductTree.pdf: ProductTree.tex
	latexmk -pdf ProductTree.tex

ProductTreeLand.tex: productlist.csv
	python makeProductTree.py --land=1

ProductTreeLand.pdf: ProductTreeLand.tex
	latexmk -pdf ProductTreeLand.tex
