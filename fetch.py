import argparse
import os
import sys

import requests


# I keep this to one file with the jobs split by function:
# fetch_starred_repositories is the only part that talks to the API,
# display_repositories only prints, and main only joins the argument
# and the token to the fetch. Keeping the network inside one function
# is what lets tests replace requests.get and check pagination, error
# handling, and headers without any live call or real token.

def fetch_starred_repositories(username, token=None):
    # GitHub API URL to fetch starred repositories
    # The username goes into the path exactly as typed, with no quoting
    # or checking. GitHub usernames only allow letters, digits, and
    # hyphens, so a normal name is safe here. A name containing a slash
    # would change the path and the API would answer for a different
    # route. I rely on GitHub's own naming rules instead of checking.
    url = f'https://api.github.com/users/{username}/starred'
    headers = {'Accept': 'application/vnd.github+json'}
    if token:
        # Personal access tokens go in the Authorization header. The token
        # is read from the environment by main() and is never printed.
        headers['Authorization'] = f'Bearer {token}'

    repositories = []
    page = 1
    while True:
        # I pass no timeout here, so a connection that opens and then
        # stalls can hold this script open for as long as the other end
        # stalls. For a script I run by hand I have accepted that. It
        # would be the first thing to fix before running this on a
        # schedule.
        # On a failure partway through, I return what I already
        # collected instead of throwing it away. The caller then prints
        # a partial list under the failure message. I prefer that to
        # losing the first hundred names because page two failed.
        try:
            response = requests.get(
                url, headers=headers, params={'per_page': 100, 'page': page}
            )
        except requests.RequestException as error:
            print(f"Failed to fetch starred repositories: {error}")
            return repositories
        if response.status_code != 200:
            print(f"Failed to fetch starred repositories. Status code: {response.status_code}")
            return repositories
        # The try above covers only the request itself. A 200 response
        # whose body is not JSON would raise out of this json call,
        # outside the handler, and crash the script. That hole is here
        # and I know it is here.
        batch = response.json()
        # A 200 body is not always a list either. An API error body is
        # a dict holding a message, and extending a list with a dict
        # would add the dict keys as if they were repositories, so I
        # stop here instead of trusting the shape.
        if not isinstance(batch, list):
            return repositories
        repositories.extend(batch)
        # A short page is the last page. The API gives me no total
        # count to aim at, so this is the only stop signal I have. The
        # cost is one extra request that comes back empty when a user
        # has an exact multiple of 100 starred repos. In my mocked run,
        # 200 repos took three calls, and the third returned an empty
        # list.
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
            name = repo.get('name') or 'No name'
            description = repo.get('description') or 'No description'
            # Stars get an is None test instead of or, on purpose: 0
            # stars is a real answer, and or would replace a real 0
            # with the fallback text. My mocked run with a star count
            # of 0 prints "Stars: 0".
            stars = repo.get('stargazers_count')
            if stars is None:
                stars = 'No star count'
            print(f"Repository: {name}")
            print(f"Description: {description}")
            print(f"Stars: {stars}")
            print('-' * 40)
    else:
        # This one message covers two cases I cannot tell apart at this
        # point: the user really has starred nothing, and the fetch
        # failed and handed me an empty list. The fetch function prints
        # its own status or error line before this, so the reason is
        # already on screen above it.
        print("No repositories found or there was an error fetching them.")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Fetch and list a GitHub user's starred repositories"
    )
    parser.add_argument("username", help="GitHub username to fetch starred repositories for")
    args = parser.parse_args(argv)

    # main is the only place that touches the environment. The fetch
    # function takes the token as a plain argument, so tests can pass a
    # dummy value or None without changing the process environment.
    # The or None turns an empty GITHUB_TOKEN into no token at all. I
    # would rather send no Authorization header than one that says
    # Bearer with nothing after it.
    token = os.environ.get('GITHUB_TOKEN') or None
    starred_repos = fetch_starred_repositories(args.username, token)
    display_repositories(starred_repos)
    # I return 0 even when the fetch failed and the list is empty. The
    # printed messages are the signal for a person reading the output.
    # Nothing about this script is built for a shell pipeline that
    # checks exit codes.
    return 0


if __name__ == "__main__":
    sys.exit(main())
