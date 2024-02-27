all: main.pdf

main.pdf: main.tex mag.bib
	latex -file-line-error -halt-on-error -interaction errorstopmode main.tex
	biber main
	pdflatex -file-line-error -halt-on-error -interaction batchmode main.tex
	pdflatex -file-line-error -halt-on-error -interaction batchmode main.tex

