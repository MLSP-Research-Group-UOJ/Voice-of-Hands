# Voice-of-Hands Journal Paper - LaTeX Source

This directory contains the LaTeX source files for the Voice-of-Hands research paper.

## Files

- **voice_of_hands_paper.tex** - Main LaTeX document containing the full paper
- **references.bib** - BibTeX bibliography file with all 28 references
- **README.md** - This file

## Compilation Instructions

### Prerequisites

Make sure you have a LaTeX distribution installed:

**Linux:**
```bash
sudo apt-get install texlive-full
```

**macOS:**
```bash
brew install --cask mactex
```

**Windows:**
Download and install MiKTeX or TeX Live from their official websites.

### Required LaTeX Packages

The paper uses the following packages (all included in texlive-full):
- IEEEtran (document class)
- cite
- amsmath, amssymb, amsfonts
- algorithmic
- graphicx
- textcomp
- xcolor
- booktabs
- multirow
- url
- hyperref
- inputenc (UTF-8)
- fontspec (for Sinhala/Tamil Unicode support)

### Compilation Commands

#### Method 1: Using the provided script (Recommended)

```bash
cd journal_paper/
./compile.sh
```

This automatically runs XeLaTeX (required for Sinhala/Tamil Unicode support) with the necessary compilation passes.

#### Method 2: Manual XeLaTeX compilation

```bash
cd journal_paper/
xelatex voice_of_hands_paper.tex
bibtex voice_of_hands_paper
xelatex voice_of_hands_paper.tex
xelatex voice_of_hands_paper.tex
```

The double compilation after bibtex ensures all cross-references and citations are properly resolved.

#### Method 3: Using latexmk (Automated)

```bash
cd journal_paper/
latexmk -xelatex voice_of_hands_paper.tex
```

This automatically runs the necessary compilation passes.

**Note:** XeLaTeX is required (not pdflatex) because the paper contains Sinhala (සිංහල) and Tamil (தமிழ்) Unicode characters that require the fontspec package.

### Output

The compilation will generate:
- **voice_of_hands_paper.pdf** - The final paper (main output)
- voice_of_hands_paper.aux - Auxiliary file
- voice_of_hands_paper.bbl - Bibliography file
- voice_of_hands_paper.blg - Bibliography log
- voice_of_hands_paper.log - Compilation log
- voice_of_hands_paper.out - Hyperref output

### Clean Build Artifacts

To clean up auxiliary files:

```bash
rm *.aux *.bbl *.blg *.log *.out *.toc
```

Or using latexmk:

```bash
latexmk -c
```

## Customization

### Author Information

Edit the `\author` block in `voice_of_hands_paper.tex`:

```latex
\author{
    \IEEEauthorblockN{Your Name\IEEEauthorrefmark{1}, Co-Author Name\IEEEauthorrefmark{2}}
    \IEEEauthorblockA{\IEEEauthorrefmark{1}Department of Computer Science, Your University, Sri Lanka\\
    Email: your.email@university.lk}
    \IEEEauthorblockA{\IEEEauthorrefmark{2}Department, Institution\\
    Email: coauthor@institution.edu}
}
```

### Adding Figures

Place figure files (PDF, PNG, JPG) in the `journal_paper/` directory and reference them:

```latex
\begin{figure}[htbp]
\centering
\includegraphics[width=0.9\columnwidth]{your_figure.pdf}
\caption{Your caption here.}
\label{fig:your_label}
\end{figure}
```

### Target Journals

This document uses the IEEE Transactions journal format (`IEEEtran` class). Suitable for submission to:

- IEEE Transactions on Multimedia
- IEEE Transactions on Pattern Analysis and Machine Intelligence
- IEEE Access
- ACM Transactions on Accessible Computing
- Computer Vision and Image Understanding
- Pattern Recognition

For other journals, you may need to change the document class and reformat accordingly.

## Paper Statistics

- **Total Pages**: ~15-18 pages (estimated, depends on figures)
- **Word Count**: ~9,500 words
- **Sections**: 6 main sections
- **Tables**: 7 tables
- **Equations**: 30+ numbered equations
- **References**: 28 citations

## Troubleshooting

### Common Issues

1. **Missing packages**: Install `texlive-full` or individual packages via your LaTeX distribution's package manager.

2. **Unicode/Sinhala rendering issues**: Make sure you're using XeLaTeX (not pdflatex). The compile script automatically uses XeLaTeX. System fonts supporting Sinhala/Tamil will be used automatically.

3. **Bibliography not appearing**: Make sure you run bibtex after the first xelatex compilation.

4. **Overfull hbox warnings**: These are usually cosmetic. Adjust text or use `\sloppy` if necessary.

## License

This work is part of the Voice-of-Hands research project. Please cite appropriately if you use or adapt this work.

## Contact

For questions about the paper content or LaTeX source, contact the corresponding author listed in the paper.

---

**Last Updated**: April 14, 2026
