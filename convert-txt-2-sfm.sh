#!/bin/env bash

infile="$1"
lang="$2"
if [[ -z $2 ]]; then
    lang="Sango"
fi
# outfile="${infile%.*}.sfm"
outfile="${HOME}/Paratext8Projects/SAB/94XXASAB.SFM"

contents=$(cat "$infile")

# Add ID.
temp="${infile}.i"
contents="\id XXA - Action Bible ($lang)
$contents"
echo "$contents" > "$temp"

# Add chapter markers.
temp="${temp}c"
echo "$contents" | sed -r 's/P([0-9]+)/\\c \1/' > "$temp"
contents=$(cat "$temp")
# Fix out-of-order chapter 254.
echo "$contents" | sed -r ':a;N;$!ba; s/\\c 254/\\c 750/2' > "$temp"
contents=$(cat "$temp")

# Add verse markers.
temp="${temp}v"
if [[ "$lang" == "Sango" ]]; then
    panel="Kapa"
elif [[ "$lang" == "English" ]]; then
    panel="Panel"
else
    echo "Error: unsupported language $lang"
    exit 1
fi
echo "$contents" | sed -r 's/'"$panel"'\s*([0-9]+)/\\v \1/' > "$temp"
contents=$(cat "$temp")

# Add paragraph markers.
temp="${temp}p"
echo "$contents" | sed -r 's/^[^\\]/\\p /' > "$temp"
contents=$(cat "$temp")

# Write out final file.
read -p "Are you sure you want to overwrite the current $outfile? [N/y]" ans
if [[ "$ans" ==  'y' ]] || [[ "$ans" == 'Y' ]]; then
    echo "$contents" > "$outfile"
else
    echo "$outfile not overwritten."
fi
