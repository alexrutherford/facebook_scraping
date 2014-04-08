Script to query Facebook API, extract public pages based on a keyword search, extract all posts and comments on posts where avaliable. Content which matches a keyword is stored.

Some complex logic is in place to handle bad requests either due to API downtime, key expiration or overuse.

Allows for restarts at a particular page.

##Outputs

1. Produces a log file _log.csv_ which records every API call and it's time. Useful for debugging and estimating usage limits.
2. Produces an output file _out.csv_ with all content that matches search terms of interest. If restarting, this file is appended to, otherwise overwrites previous content.

##Arguments

1. To restart at a specific page (if for example, token expired midway through looping through a large collection of search results) run with page ID as a single argument. Will skip over other pages until it matches

2. To restart at a specific page _and_ a specific set of posts on that page, call with two arguments. First is page ID as above and second is link to that page via API. This link is recorded in log file and can be used to restart when middway through a specific page of posts from a given page.

##Requirements

Requires [requests library](http://docs.python-requests.org/en/latest/)
