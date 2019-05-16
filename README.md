# tips_n_tricks
Collection of scripts, snippets, etc, that I find useful


# awk
* removing the last character in field 2 - substr - 
`{print substr($2, 1, length($2)-1)}`
