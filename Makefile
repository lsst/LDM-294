export TEXMFHOME ?= lsst-texmf/texmf

TEX=DDMP.tex LDM-294.tex devprocess.tex dmarc.tex dmgroups.tex dmorg.tex dmproducts.tex dmroles.tex dmwbs.tex intro.tex leadtutes.tex probman.tex productlist.tex wbslist.tex

MKPDF=latexmk -pdf

GENERATED_FIGURES=ProductTree.pdf ProductTreeLand.pdf
GENERATED_FIGURES_TEX=$(GENERATED_FIGURES:.pdf=.tex)
PRODUCT_CSV=DM\ Product\ Properties.csv
DOC=LDM-294
SRC=$(DOC).tex
all: $(DOC).pdf

LDM-294.pdf: *.tex wbslist.tex ${GENERATED_FIGURES} aglossary.tex
	$(MKPDF) -bibtex -f $(SRC)
	makeglossaries $(DOC)        
	xelatex  $(SRC)



#Run with -u manually to put \gls on glossary entries 
aglossary.tex:  ${TEX} myacronyms.txt skipacronyms.txt
	$(TEXMFHOME)/../bin/generateAcronyms.py  -g -t "DM"  devprocess.tex dmarc.tex dmorg.tex dmroles.tex leadtutes.tex probman.tex  aglossary.tex 

wbslist.tex: makeWbs.py wbs/*tex ${PRODUCT_CSV}
	python makeWbs.py ${PRODUCT_CSV}

ProductTree.tex: makeProductTree.py ${PRODUCT_CSV}
	python --version
	python makeProductTree.py --depth=2 --file=${PRODUCT_CSV}

ProductTree.pdf: ProductTree.tex
	$(MKPDF) $<

ProductTreeLand.tex: makeProductTree.py ${PRODUCT_CSV}
	python makeProductTree.py --land=2 --file=${PRODUCT_CSV}

ProductTreeLand.pdf: ProductTreeLand.tex
	$(MKPDF) $<

# productlist.tex is generated as a by-product of making ProductTree.tex.
productlist.tex: ProductTree.tex

# These targets are designed to be used by Travis
# so that we can control when python will be called.
# "generated" can call python.
generated: $(GENERATED_FIGURES_TEX) wbslist.tex aglossary.tex

# "travis-all" must only call Latex
travis-all: *.tex
	for f in $(GENERATED_FIGURES_TEX); do $(MKPDF) "$$f" ; done
	$(MKPDF) -bibtex -f LDM-294

clean :
	latexmk -c
	rm *.pdf *.nav *.bbl *.xdv *.snm
