# pubmed_jekyll
Uses `biopython` package in Python (3.x+) to search for all papers by a given author to populate a .yml file for Jekyll static pages. 

Pubmed search for citations from author in Pubmed using Biopython package for
populating a .yml file for Jekyll page templates.
This will create a `./_data/` folder as is common in Jekyll sites.

Retreives the following info:
- Authors: Last and Forename of first author. If fewer than 4 authors, list all.
- Article Information: Title.
- Journal Information: Journal abbreviation, Volume, Issue, Pagination (if present) and year.
- DOI Link if it exists.
- Abstract Text: Only in --verbose mode, and will only be printed (not in yml file)

Saves information to _data/papers.yml unless `--do_not_populate` (only prints results)

Usage:

1. Straight from Python.  
`>>> python pubmed_author_papers.py email@domain.com 'LastName AB' --max 10 -v -d`

2. Using the bash file (please change the `search.sh` file information to suit your needs).  
`>>> bash search.sh`

Arguments:  
`email` str - Valid email for use of NCBI database search.  
`author` str - Author information formatted "LastName INITIALS".  
`--max` int - Maximum number of articles to search.  
`-v` `--verbose` - If specified, print out article information.  
`-d` `--do_not_populate` - If specified, will not populate the papers.yml  
