export TEXMFHOME = lsst-texmf/texmf

LDM-294.pdf: *.tex
	latexmk -bibtex -pdf -f LDM-294.tex
