(TeX-add-style-hook
 "main"
 (lambda ()
   (TeX-add-to-alist 'LaTeX-provided-package-options
                     '(("fontenc" "T1") ("biblatex" "backend=biber" "style=numeric" "sorting=ynt")))
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-braces-local "path")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "url")
   (add-to-list 'LaTeX-verbatim-macros-with-delims-local "path")
   (TeX-run-style-hooks
    "latex2e"
    "sections/intro"
    "sections/literature"
    "sections/solution"
    "sections/experiments"
    "sections/summary"
    "pginz"
    "pginz10"
    "subcaption"
    "indentfirst"
    "fontenc"
    "csquotes"
    "biblatex"
    "float"
    "framed"
    "amsmath"
    "dirtytalk")
   (TeX-add-symbols
    '("mref" 1)
    '("todo" 1)
    '("ang" 1))
   (LaTeX-add-bibliographies
    "mag"))
 :latex)

