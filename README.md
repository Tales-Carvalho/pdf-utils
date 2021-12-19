# PDF Utils

TODO

- GS support snippet (compresses all PDF files in a folder - thanks to https://gist.github.com/firstdoit/6390547#gistcomment-3249448):
```bash
find . -name '*.pdf' | while read pdf; do gs -q -dNOPAUSE -dBATCH -sDEVICE=pdfwrite -dCompatibilityLevel=1.4 -dPDFSETTINGS=/screen -dEmbedAllFonts=true -dSubsetFonts=true -dAutoRotatePages=/None -dColorImageDownsampleType=/Bicubic -dColorImageResolution=150 -dGrayImageDownsampleType=/Bicubic -dGrayImageResolution=150 -dMonoImageDownsampleType=/Bicubic -dMonoImageResolution=150 -sOutputFile="${pdf}_new.pdf" "$pdf"; done
```
- Adjust the "150" resolution for different results
