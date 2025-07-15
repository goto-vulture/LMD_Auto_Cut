#!/bin/bash

fileOne="Main_Function_Seq_Diagram"
umlLatexFile="tikz-uml.sty"

# Check whether the tikz-uml.sty file is available?
if [[ ! -f "${umlLatexFile}" || ! -r "${umlLatexFile}" ]]; then
    echo "The ${umlLatexFile} is not available."
    echo "You can find the file here: https://perso.ensta-paris.fr/~kielbasi/tikzuml/index.php?lang=en"
    exit 1
fi

if ! command -v pdflatex >/dev/null 2>&1; then
    echo "pdflatex for the tex translation is not available."
    exit 2
fi

rm "${fileOne}.pdf"
time pdflatex -no-shell-escape -interaction nonstopmode "${fileOne}.tex"
rm "${fileOne}.log" "${fileOne}.aux"

# evince "${fileOne}.pdf"
