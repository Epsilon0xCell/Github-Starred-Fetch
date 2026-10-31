import argparse
import os
import re
import sys

import requests


# I keep this to one file with the jobs split by function:
# fetch_starred_repositories is the only part that talks to the API,
# display_repositories only prints, and main only joins the argument
# and the token to the fetch. Keeping the network inside one function
# is what lets tests replace requests.get and check pagination, error
# handling, and headers without any live call or real token.

# GitHub usernames are letters, digits, and single hyphens, 1 to 39
# characters, and cannot start or end with a hyphen. I check the shape
# here instead of relying on it: a name containing a slash would
# change the API path and the API would answer for a different route.
USERNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$")

# A stalled connection should not hold a hand run script open for as
# long as the other end stalls, so every request gets this timeout.
REQUEST_TIMEOUT = 15


class FetchError(Exception):
    """The API did not give a usable answer. The message is printed
    by main, and the run exits 1, so a shell pipeline can tell a
    failed fetch from a user who has starred nothing."""


def fetch_starred_repositories(username, token=''):
    """Return the full list of repositories username has starred.

    Raises FetchError on a network failure, a non-200 status, or a
    200 body that is not a JSON list of repositories. Earlier versions
    returned whatever had been collected before a failure, so a
    partial list printed under an error line and the run still exited
    0; a caller could not tell complete output from a cut off one.
    """
    url = f"https://api.github.com/users/{username}/starred"
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        # Personal access tokens go in the Authorization header. The token
        # is read from the environment by main() and is never printed.
        headers["Authorization"] = f"Bearer {token}"

    repositories = []
    page = 1
    while True:
        try:
            response = requests.get(
                url,
                headers=headers,
                params={"per_page": 100, "page": page},
                timeout=REQUEST_TIMEOUT,
            )
        except requests.RequestException as error:
            raise FetchError(f"Failed to fetch starred repositories: {error}") from error
        if response.status_code != 200:
            raise FetchError(
                f"Failed to fetch starred repositories. Status code: {response.status_code}"
            )
        try:
            batch = response.json()
        except ValueError as error:
            raise FetchError(
                "Failed to fetch starred repositories: response was not JSON"
            ) from error
        # A 200 body is not always a list. An API error body is a dict
        # holding a message, and extending a list with a dict would
        # add the dict keys as if they were repositories.
        if not isinstance(batch, list):
            raise FetchError(
                "Failed to fetch starred repositories: response was not a list"
            )
        repositories.extend(batch)
        # A short page is the last page. The API gives me no total
        # count to aim at, so this is the only stop signal I have. The
        # cost is one extra request that comes back empty when a user
        # has an exact multiple of 100 starred repos.
        if len(batch) < 100:
            return repositories
        page += 1


def display_repositories(repositories):
    # Print details of each starred repository
    if repositories:
        for repo in repositories:
            # I use or for name and description, not a default value in
            # get. GitHub sends null for a repo with no description, and
            # a get default only helps when the key is missing entirely,
            # so the first version of this printed the word None. The
            # or form also turns an empty string description into the
            # fallback text, which is what I want on screen.
            name = repo.get("name") or "No name"
            description = repo.get("description") or "No description"
            # Stars get an is None test instead of or, on purpose: 0
            # stars is a real answer, and or would replace a real 0
            # with the fallback text.
            stars = repo.get("stargazers_count")
            if stars is None:
                stars = "No star count"
            print(f"Repository: {name}")
            print(f"Description: {description}")
            print(f"Stars: {stars}")
            print("-" * 40)
    else:
        print("No repositories found.")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Fetch and list a GitHub user's starred repositories"
    )
    parser.add_argument("username", help="GitHub username to fetch starred repositories for")
    args = parser.parse_args(argv)

    if not USERNAME_RE.match(args.username):
        print(f"Error: {args.username!r} is not a valid GitHub username.", file=sys.stderr)
        return 2

    # main is the only place that touches the environment. The fetch
    # function takes the token as a plain argument, so tests can pass a
    # dummy value or None without changing the process environment.
    # The or None turns an empty GITHUB_TOKEN into no token at all. I
    # would rather send no Authorization header than one that says
    # Bearer with nothing after it.
    auth = os.environ.get('GITHUB_TOKEN') or ''
    try:
        starred_repos = fetch_starred_repositories(args.username, auth)
    except FetchError as error:
        print(str(error), file=sys.stderr)
        return 1
    display_repositories(starred_repos)
    return 0


if __name__ == "__main__":
    sys.exit(main())
