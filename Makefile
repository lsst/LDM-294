export TEXMFHOME = lsst-texmf/texmf

TEX=DDMP.tex	dmgroups.tex	dmroles.tex	leadtutes.tex	probman.tex LDM-294.tex	devprocess.tex	dmorg.tex	dmwbs.tex dmarc.tex	dmproducts.tex intro.tex productlist.tex

MKPDF=latexmk -pdf

GENERATED_FIGURES=ProductTree.pdf ProductTreeLand.pdf
GENERATED_FIGURES_TEX=$(GENERATED_FIGURES:.pdf=.tex)
PRODUCT_CSV=DM\ Product\ Properties.csv

all : LDM-294.pdf

LDM-294.pdf: *.tex wbslist.tex ${GENERATED_FIGURES}
	$(MKPDF) -bibtex -f LDM-294.tex

acronyms.tex:  ${TEX} myacronyms.txt
	$(TEXMFHOME)/../bin/generateAcronyms.py  ${TEX}

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
generated: $(GENERATED_FIGURES_TEX) wbslist.tex

# "travis-all" must only call Latex
travis-all: *.tex
	for f in $(GENERATED_FIGURES_TEX); do $(MKPDF) "$$f" ; done
	$(MKPDF) -bibtex -f LDM-294
