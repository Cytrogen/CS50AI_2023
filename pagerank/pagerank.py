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

    # Initialize transition model
    model = {page: 0 for page in corpus}

    # Get all pages in corpus
    pages = list(corpus.keys())

    # Get all pages linked to by current page
    links = list(corpus[page])

    # Calculate probability of choosing a link at random
    random_prob = (1 - damping_factor) / len(pages)

    # If current page has no links, choose from all pages in corpus
    if len(links) == 0:
        links = pages
    else:
        pass

    # Calculate probability of choosing a link at random from current page (or all pages if no links)
    linked_prob = damping_factor / len(links)

    # Update transition model
    for page in pages:
        model[page] += random_prob
    for page in links:
        model[page] += linked_prob

    return model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Initialize all page ranks to 0
    page_rank = {page: 0 for page in corpus}

    # Choose a page at random to start
    page = random.choice(list(corpus.keys()))

    # Iterate n times
    for i in range(n):
        # Update page rank
        page_rank[page] += 1

        # Get transition model for current page
        model = transition_model(corpus, page, damping_factor)

        # Choose next page
        page = random.choices(list(model.keys()), weights=list(model.values()), k=1)[0]

    # Normalize page ranks
    for page in page_rank:
        page_rank[page] /= n

    return page_rank


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """

    # Initialize all page ranks to 1/N
    links_num = len(corpus)
    ranks = {page: 1 / links_num for page in corpus}

    # Iterate until convergence
    while True:
        # Create a copy of current ranks to check for convergence
        new_ranks = ranks.copy()

        # Iterate over each page in corpus
        for page in corpus:
            # Calculate and update new rank for current page
            ranks[page] = (1 - damping_factor) / links_num
            for linking_page in corpus:
                if page in corpus[linking_page]:
                    ranks[page] += damping_factor * new_ranks[linking_page] / len(corpus[linking_page])

        # Check for convergence
        if all(abs(ranks[page] - new_ranks[page]) < 0.001 for page in corpus):
            break

    return ranks


if __name__ == "__main__":
    main()
