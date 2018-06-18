export TEXMFHOME = lsst-texmf/texmf

TEX=DDMP.tex	dmgroups.tex	dmroles.tex	leadtutes.tex	probman.tex LDM-294.tex	devprocess.tex	dmorg.tex	dmwbs.tex dmarc.tex	dmproducts.tex	intro.tex

MKPDF=latexmk -pdf

GENERATED_FIGURES=ProductTreeLand.pdf ProductTree.pdf
GENERATED_FIGURES_TEX=$(GENERATED_FIGURES:.pdf=.tex)
PRODUCT_CSV=DM\ Product\ Properties.csv

all : LDM-294.pdf

LDM-294.pdf: *.tex wbslist.tex ${GENERATED_FIGURES}
	$(MKPDF) -bibtex -f LDM-294.tex

acronyms: acronyms.csh ${TEX} myacronyms.tex
	acronyms.csh  ${TEX}

wbslist.tex: makeWbs.py wbs/*tex ${PRODUCT_CSV}
	python makeWbs.py ${PRODUCT_CSV}

ProductTree.tex: makeProductTree.py ${PRODUCT_CSV}
	python --version
	python makeProductTree.py --depth=3 --file=${PRODUCT_CSV}

ProductTree.pdf: ProductTree.tex
	$(MKPDF) $<

ProductTreeLand.tex: makeProductTree.py ${PRODUCT_CSV}
	python makeProductTree.py --land=1

ProductTreeLand.pdf: ProductTreeLand.tex
	$(MKPDF) $<

# These targets are designed to be used by Travis
# so that we can control when python will be called.
# "generated" can call python.
generated: $(GENERATED_FIGURES_TEX) wbslist.tex

# "travis-all" must only call Latex
travis-all: *.tex
	for f in $(GENERATED_FIGURES_TEX); do $(MKPDF) "$$f" ; done
	$(MKPDF) -bibtex -f LDM-294
