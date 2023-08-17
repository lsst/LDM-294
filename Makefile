export TEXMFHOME ?= lsst-texmf/texmf

TEX=DDMP.tex LDM-294.tex devprocess.tex dmarc.tex dmgroups.tex dmorg.tex dmproducts.tex dmroles.tex dmwbs.tex intro.tex leadtutes.tex probman.tex productlist.tex wbslist.tex

MKPDF=latexmk -pdf

GENERATED_FIGURES=ProductTree.pdf ProductTreeLand.pdf gantt.pdf
GENERATED_FIGURES_TEX=$(GENERATED_FIGURES:.pdf=.tex)
PRODUCT_CSV=DM\ Product\ Properties.csv
DOC=LDM-294
SRC=$(DOC).tex
all: $(DOC).pdf

LDM-294.pdf: *.tex wbslist.tex ${GENERATED_FIGURES} aglossary.tex 
	xelatex $(DOC)
	makeglossaries $(DOC)
	bibtex $(DOC)
	$(MKPDF) -bibtex -f $(SRC)
	makeglossaries $(DOC)
	xelatex $(DOC)
	xelatex $(DOC)

reqinst.txt:
	touch reqinst.txt
	pip install -r requirements.txt
	pip install -r milestones/requirements.txt

gantt.tex:
	PYTHONPATH=milestones python milestones/milestones.py   gantt

gantt.pdf: gantt.tex
	pdflatex gantt.tex	

# Run with -u manually to put \gls on glossary entries
# Note need to run multiple times to recursively expand all glossary entries!
aglossary.tex:  ${TEX} myacronyms.txt skipacronyms.txt
	$(TEXMFHOME)/../bin/generateAcronyms.py  -g -t "DM Gen"  $(TEX)

wbslist.tex: makeWbs.py wbs/*tex ${PRODUCT_CSV} reqinst.txt
	python makeWbs.py ${PRODUCT_CSV}

ProductTree.tex: makeProductTree.py ${PRODUCT_CSV} reqinst.txt
	python --version
	python makeProductTree.py --depth=2 --file=${PRODUCT_CSV}

ProductTree.pdf: ProductTree.tex reqinst.txt 
	$(MKPDF) $<

ProductTreeLand.tex: makeProductTree.py ${PRODUCT_CSV} reqinst.txt
	python makeProductTree.py --land=2 --file=${PRODUCT_CSV}

ProductTreeLand.pdf: ProductTreeLand.tex reqinst.txt
	$(MKPDF) $<

# productlist.tex is generated as a by-product of making ProductTree.tex.
productlist.tex: ProductTree.tex

# These targets are designed to be used by Travis
# so that we can control when python will be called.
# "generated" can call python.
generated: $(GENERATED_FIGURES_TEX) wbslist.tex aglossary.tex reqinst.txt

# "travis-all" must only call LaTeX & associated commands (makeglossaries,
# latexmk, etc).
travis-all: *.tex
	for f in $(GENERATED_FIGURES_TEX); do $(MKPDF) "$$f" ; done
	xelatex LDM-294
	makeglossaries LDM-294
	$(MKPDF) -bibtex -f LDM-294
	makeglossaries $(DOC)
	xelatex $(DOC)
	xelatex $(DOC)

clean :
	latexmk -c
	rm -f *.pdf *.nav *.bbl *.xdv *.snm *.gls *.glg *.glo
