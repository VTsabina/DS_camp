#!/bin/sh

INPUT="../ex02/hh_sorted.csv"
OUTPUT="hh_positions.csv"

head -n 1 "$INPUT" > "$OUTPUT"

tail -n +2 "$INPUT" | sed 's/",/#/g; s/,"/#/g'| while IFS='#' read -r id created_at name has_test alternate_url; do
{
    grades=()
    [[ "$name" =~ [jJ]unior ]] && grades+=("Junior")
    [[ "$name" =~ [mM]iddle ]] && grades+=("Middle")
    [[ "$name" =~ [sS]enior ]] && grades+=("Senior")

    if [ ${#grades[@]} -gt 0 ]; then
        new_name=$(IFS=/; echo "${grades[*]}")
    else
        new_name="-"
    fi

    echo "$id\",$created_at\",\"$new_name\",\"$has_test\",\"$alternate_url" >> "$OUTPUT"
}
done