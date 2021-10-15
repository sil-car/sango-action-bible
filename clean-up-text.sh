#!/usr/bin/env bash

# Use sed to remove various unwanted characters from text file, in preparation for
#   converting the text file to SFM.

infile="${1}"
outfile="${infile%.txt}_clean.txt"
contents=$(cat "$infile")

replace() {
    local f="$1"
    local r="$2"
    # echo "pat: \"$pat\""

    echo "$contents" | sed -r 's@'"$f"'@'"$r"'@' > "$outfile"
    contents=$(cat "$outfile")
}

replace_nth_occurrance() {
    local n="$1"
    local pat="$2"

    echo "$contents" | sed -r ":a;N;\$!ba; ${pat}${n}" > "$outfile"
    contents=$(cat "$outfile")
}

# Remove work records ##/##/##.
replace '[0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}.*$'

# Remove all xxx### markers.
replace 'xxx[0-9]+\s*\n'

# Remove lines that are only all-caps and/or spaces.
replace '^[A-Z ]+$'

# Remove "TO EXODUS 32" (A-Z, 0-9, ' '; 5 or more characters).
replace '[A-Z0-9 ]{5,}'

# Fix out-of-order chapter 254.
replace_nth_occurrance 2 's/P254/P750/'

# Fix poorly-formatted page numbers.
replace '^[\s]*p([0-9]{2,3})' 'P\1'

# Remove non-breaking spaces that begin lines.
replace '^\xC2\xA0'

# Remove extra blank lines.
perl -0777pi -e 's/\n{2,}/\n/g' "$outfile"
