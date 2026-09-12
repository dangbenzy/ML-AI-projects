import os
import random
import re
import sys

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """

    # Number of pages
    N = len(corpus.keys())
    pages = set(corpus.keys())

    # Number of links
    i = len(corpus[page])

    # Output
    output = {}

    if i == 0:
        d = 1/N
        for page in pages:
            output[page] = d
        return output

    elif i > 0:
        d = (1-damping_factor)/N
        for pg in (pages-corpus[page]):
            output[pg] = d
        for link in corpus[page]:
            output[link] = d + (damping_factor/i)
        return output

    raise NotImplementedError


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = list(corpus.keys())
    counter = {}
    output = {}
    for page in pages:
        counter[page] = 0
    page = random.choice(pages)
    counter[page] = 1
    model = transition_model(corpus, page, damping_factor)
    x = 1
    while x < n:
        # Make a single prediction and increment counter
        sample = random.choices(list(model.keys()), weights=list(model.values()), k=1)[0]
        model = transition_model(corpus, sample, damping_factor)
        for page in pages:
            if page == sample:
                counter[page] += 1
                break
        x += 1
    # sampling
    for page, freq in counter.items():
        output[page] = freq/n

    return output

    raise NotImplementedError


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pages = set(corpus.keys())
    N = len(pages)
    oldrank = {}

    d = 1/N
    x = 0
    for page in pages:
        oldrank[page] = d
    # print(oldrank)
    corpuss = corpus.copy()
    for page in corpuss:
        if len(corpuss[page]) == 0:
            corpuss[page] = pages

    while True:
        newrank = {}
        # select a page

        for page in pages:
            total = 0
            # caculate total for the page' that links to page
            for eachpage in corpuss:
                if page in corpuss[eachpage]:
                    total += oldrank[eachpage]/len(corpuss[eachpage])

            if all(page not in corpuss[eachpage] for eachpage in corpuss):
                for page in pages:
                    total += oldrank[page]/N
            newrank[page] = ((1-damping_factor)/N)+(damping_factor*total)

        if all(abs(oldrank[page]-newrank[page]) <= 0.001 for page in pages):
            # All values are less than or equal to 1
            return newrank
        oldrank = newrank.copy()

    raise NotImplementedError


if __name__ == "__main__":
    main()
