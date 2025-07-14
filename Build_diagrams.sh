#!/bin/bash

fileOne="Main_Function_Seq_Diagram"

rm "${fileOne}.pdf"
time pdflatex -no-shell-escape -interaction nonstopmode "${fileOne}.tex"
rm "${fileOne}.log" "${fileOne}.aux"

evince "${fileOne}.pdf"
