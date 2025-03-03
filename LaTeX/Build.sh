time pdflatex Main
time makeindex -s Main.ist -o Main.gls Main.glo
time bibtex Main
time pdflatex Main
time pdflatex Main
