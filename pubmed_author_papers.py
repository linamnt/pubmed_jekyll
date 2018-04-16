"""
Author: Lina Tran @linamnt
Date: March 15, 2018

Pubmed search for citations from author in Pubmed using Biopython package for
populating a .yml file for Jekyll page templates.
Requires a ./_data/ folder as is common in Jekyll sites.

Retreives the following info:
- Authors: Last and Forename of first author. If fewer than 4 authors, list all.
- Article Information: Title.
- Journal Information: Journal abbreviation, Volume, Issue, Pagination (if present) and year.
- DOI Link if it exists.
- Abstract Text: Only in --verbose mode, and will only be printed (not in yml file)

Saves information to _data/papers.yml unless --verbose (only prints results)

Usage:

>>> python pubmed_author_papers.py email@domain.com 'LastName AB' --max 10 -v -d

Arguments:
email str - Valid email for use of NCBI database search.
author str - Author information formatted "LastName INITIALS".
--max int - Maximum number of articles to search.
-v --verbose - If specified, print out article information.
-d --do_not_populate - If specified, will not populate the papers.yml

"""

from Bio import Entrez
import argparse


def parse_author(author_info):
    '''
    Takes a pubmed entry's author info and returns lastname, forename.
    '''
    last = author_info['LastName']
    forename = author_info['ForeName']
    name = ", ".join([last, forename])
    return name


def parse_journal(journal_info, pagination):
    '''
    Takes a pubmed entry's journal publication info and returns issue information.
    '''
    abbrev = journal_info['ISOAbbreviation']

    if 'JournalIssue' in journal_info:
        issue = journal_info['JournalIssue']
        if pagination and 'Issue' in issue:
            issue = ', '.join([abbrev, issue['Volume'], issue['Issue'], pagination['MedlinePgn']])
        else:
            issue = ', '.join([abbrev, issue['Volume']])
    else:
        issue = abbrev
    return issue


class Paper(object):
    def __init__(self, pubmed_entry):
        """
        Takes a pubmed_entry and parses information to make a yml attribute
        formatted as follows:
        - author:
          title: Title and Journal Issue Info
          alt_link: https://doi.org/DOI_INFO (if it exists)
          year: Year citation was published
        """
        article_info = pubmed_entry['MedlineCitation']['Article']
        #author info
        authors = article_info['AuthorList']
        if "Abstract" in article_info:
            self.abstract = article_info['Abstract']
        else:
            self.abstract = ''
        if len(authors) < 3:
            self.first_author = ', '.join([parse_author(author) for author in authors]) + '.'
        else:
            self.first_author = parse_author(authors[0]) + ' et al.'
        #article info
        if len(article_info['ArticleDate']):
            self.year = article_info['ArticleDate'][0]['Year']
        else:
            try:
                self.year = article_info['Journal']['JournalIssue']['PubDate']['Year']
            except KeyError:
                self.year = ''
        self.title = article_info['ArticleTitle']
        pagination = False
        if "Pagination" in article_info:
            pagination = article_info['Pagination']
        self.journal_info = parse_journal(article_info['Journal'], pagination)
        if len(article_info["ELocationID"]):
            self.link = 'https://doi.org/' + article_info['ELocationID'][0]
        else:
            self.link = ''
        print(self.first_author, self.title, self.link, self.journal_info)
        self.yml = "- author: {}\n  title: '{} {}.'\n  alt_link: '{}'\n  year: {}\n\n".format(self.first_author, self.title, self.journal_info, self.link, self.year)
        self.long_print = "author: {}\nyear: {}\ntitle: '{} \n{}.'\nabstract: '{}'\nDOI_link: '{}'\n\n".format(self.first_author, self.year, self.title, self.journal_info, self.abstract, self.link, )


def search_author(query, email, max_search=20):
    Entrez.email = email
    handle = Entrez.esearch(db='pubmed',
                            retmax=max_search,
                            retmode='XML',
                            term=query)
    results = Entrez.read(handle)
    return results['IdList']



def fetch_details(id_list, email):
    ids = ','.join(id_list)
    Entrez.email = email
    handle = Entrez.efetch(db='pubmed',
                           retmode='xml',
                           id=ids)
    results = Entrez.read(handle)
    return results['PubmedArticle']

def fetch_new_papers(ids, email, verbose=False):
    '''
    Fetch only new papers, and update the recent_pubmed_ids.txt list.
    If no new papers found, stop.
    '''
    try:
        a = open('_data/recent_pubmed_ids.txt', 'r')
        previous_ids = a.read().split(',')
        a.close()
    except IOError:
        a = open('_data/recent_pubmed_ids.txt', 'w')
        previous_ids = []
        a.close()

    ids_new = [i for i in ids if i not in previous_ids]
    all_ids = ids_new + previous_ids

    if verbose:
        results = fetch_details(ids, email)
        return [Paper(i).long_print for i in results]
    elif len(ids_new):
        #only fetch if there are new ids
        results = fetch_details(ids_new, email)
        papers = [Paper(i).yml for i in results]


        #update recent_pubmed_ids
        a = open('_data/recent_pubmed_ids.txt', 'w')
        a.write(','.join(all_ids))
        a.close()

        return papers
    else:
        print("No new papers found.")


def add_new_papers(new_papers):
    if new_papers:
        append_copy = open("_data/papers.yml", "r")
        original_text = append_copy.read()
        append_copy.close()

        new_papers = ''.join(new_papers)

        append_copy = open("_data/papers.yml", "w")
        append_copy.write(new_papers)
        append_copy.write(original_text)
        append_copy.close()


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("email", help="Write email to use for pubmed search", type=str)
    parser.add_argument("author", help="Name of author to search in the form 'Last INITIALS'", type=str)
    parser.add_argument("--max", help="Max number of articles to retrieve, default=20", default=20, type=int)
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("-d", "--do_not_populate", action="store_true")

    args = parser.parse_args()
    return args


def main():
    # parse arguments
    args = get_args()
    user_email = args.email
    author = args.author + '[Author]'

    # search the author, find paper details and add to papers.yml

    # load the papers already retrieved in the past if they exist,
    # else create papers.yml
    try:
        append_copy = open("_data/papers.yml", "r")
        current_papers = append_copy.read()
        append_copy.close()
    except IOError:
        papers_yml = open('_data/papers.yml', 'w')
        current_papers = []
        papers_yml.close()

    # if current papers is empty, search for all papers, default max is 100
    # change if the number of papers may be more
    # this only retrieves the paper IDs
    if len(current_papers):
        ids = search_author(author, user_email, args.max)
    else:
        ids = search_author(author, user_email, args.max if args.max else 100)
    if len(ids) == 0:
        return
    # only fetch paper information for IDs not already in papers.yml
    if args.verbose:
        papers = fetch_new_papers(ids, user_email, args.verbose)
        for paper in papers:
            print(paper)
    if not args.do_not_populate:
        papers = fetch_new_papers(ids, user_email)
        if papers is not None:
            add_new_papers(papers)
            print("Added {} new papers.".format(len(papers)))

if __name__ == '__main__':
    main()
