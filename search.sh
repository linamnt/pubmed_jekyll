#!/bin/sh

EMAIL='email@domain.ca'
AUTHOR="LASTNAME INITIALS"
MAX_SEARCH=20

#check if _data/ folder exists, otherwise create it
mkdir -p _data
#add -d to NOT populate the datafiles, -v to print out verbose abstracts into STDOUT
python pubmed_author_papers.py $EMAIL "$AUTHOR" --max $MAX_SEARCH -d -v
