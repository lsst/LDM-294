export TEXMFHOME = lsst-texmf/texmf

LDM-294.pdf: *.tex
	latexmk -bibtex -pdf -f LDM-294.tex

acronyms:*.tex
	acronyms.csh DDMP.tex	dmgroups.tex	dmroles.tex	leadtutes.tex	probman.tex LDM-294.tex	devprocess.tex	dmorg.tex	dmwbs.tex dmarc.tex	dmproducts.tex	intro.tex	
