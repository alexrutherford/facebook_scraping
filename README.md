Script to query Facebook API, extract public pages based on a keyword search, extract all posts and comments on posts where avaliable. Content which matches a keyword is stored.

Some complex logic is in place to handle bad requests either due to API downtime, key expiration or overuse.

Allows for restarts at a particular page.

**Requirements

Requires requests library
