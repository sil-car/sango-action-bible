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
    local f="$2"
    local r="$3"

    echo "$contents" | sed -r ":a;N;\$!ba; s@${f}@${r}@${n}" > "$outfile"
    contents=$(cat "$outfile")
}

# Remove non-breaking spaces that begin lines.
replace '^\xC2\xA0'

# Remove work records ##/##/##.
replace '[0-9]{1,2}/[0-9]{1,2}/[0-9]{1,2}.*$'

# Remove all xxx### markers.
replace 'xxx[0-9]+\s*\n'

# COMMENTED OUT B/C WANTED TO PRESERVE THESE ARTIFACTS.
# Remove lines that are only all-caps and/or spaces.
# replace '^[A-Z ]+$'

# COMMENTED OUT B/C TOO GREEDY.
# Remove "TO EXODUS 32" (A-Z, 0-9, ' '; 5 or more characters).
# replace '[A-Z0-9 ]{5,}'

# Fix out-of-order chapter 254.
replace_nth_occurrance 2 'P254' 'P750'

# Fix poorly-formatted page numbers.
replace '^p([0-9]{2,3})' 'P\1'

# Fix mis-numbered page numbers.
replace 'P318' 'P320'
replace 'P317' 'P319'
replace_nth_occurrance 2 'P316' 'P318'
replace_nth_occurrance 2 'P315' 'P317'
replace_nth_occurrance 2 'P563' 'P564'
replace 'P748' 'P749'
replace_nth_occurrance 2 'P747' 'P748'

# Remove extra blank lines.
perl -0777pi -e 's/\n{2,}/\n/g' "$outfile"
