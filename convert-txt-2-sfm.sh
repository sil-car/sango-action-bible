#!/bin/env bash

infile="$1"
# Infile should end like this: _en-US_clean.txt.
if [[ "${infile: -16}" != '_en-US_clean.txt' ]] && [[ "${infile: -16}" != '_sg-CF_clean.txt' ]]; then
    echo "Error: file name should end with \"_en-US_clean.txt\""
    exit 1
fi
temp="${infile}.tmp"
stem="${infile%.txt}"
part="${stem%_*}"
lang="${part##*_}"

# Set output file name and path.
if [[ "$lang" == 'sg-CF' ]]; then
    name="SAB"
    filename="94XXA${name}.SFM"
    panel="Kapa"
elif [[ "$lang" == 'en-US' ]]; then
    name="EAB"
    filename="94XXA${name}.SFM"
    panel="Panel"
fi
outfile="${HOME}/Paratext8Projects/${name}/${filename}"

# Get contents of input file.
contents=$(cat "$infile")

# Add ID.
contents="\id XXA - Action Bible ($lang)
$contents"
echo "$contents" > "$temp"

# Add chapter markers.
echo "$contents" | sed -r 's/P([0-9]+)/\\c \1/' > "$temp"
contents=$(cat "$temp")
# Fix out-of-order chapter 254.
echo "$contents" | sed -r ':a;N;$!ba; s/\\c 254/\\c 750/2' > "$temp"
contents=$(cat "$temp")

# Add verse markers.
echo "$contents" | sed -r 's/'"$panel"'\s*([0-9]+)/\\v \1/' > "$temp"
contents=$(cat "$temp")

# Add paragraph markers.
echo "$contents" | sed -r 's/^([^\\])/\\p \1/' > "$temp"
contents=$(cat "$temp")

# Write out final file.
if [[ -e "$outfile" ]]; then
    read -p "Are you sure you want to overwrite the current $outfile? [y/N]: " ans
    if [[ "$ans" ==  'y' ]] || [[ "$ans" == 'Y' ]]; then
        echo "$contents" > "$outfile"
    else
        echo "$outfile not overwritten."
    fi
else
    echo "$contents" > "$outfile"
fi

# Ask to keep temp file.
read -p "Keep $temp? [y/N]: " ans
if [[ "$ans" == 'y' ]] || [[ "$ans" == 'Y' ]]; then
    exit 0
fi
rm -f "$temp"
