all: main.pdf

main.pdf: main.tex mag.bib
	latex -file-line-error -halt-on-error main.tex
	biber main
	pdflatex -file-line-error -halt-on-error main.tex
	pdflatex -file-line-error -halt-on-error main.tex

