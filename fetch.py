import argparse
import os
import sys

import requests


def fetch_starred_repositories(username, token=None):
    # GitHub API URL to fetch starred repositories
    url = f'https://api.github.com/users/{username}/starred'
    headers = {'Accept': 'application/vnd.github+json'}
    if token:
        # Personal access tokens go in the Authorization header. The token
        # is read from the environment by main() and is never printed.
        headers['Authorization'] = f'Bearer {token}'

    repositories = []
    page = 1
    while True:
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
        batch = response.json()
        if not isinstance(batch, list):
            return repositories
        repositories.extend(batch)
        # A short page is the last page.
        if len(batch) < 100:
            return repositories
        page += 1


def display_repositories(repositories):
    # Print details of each starred repository
    if repositories:
        for repo in repositories:
            name = repo.get('name') or 'No name'
            description = repo.get('description') or 'No description'
            stars = repo.get('stargazers_count')
            if stars is None:
                stars = 'No star count'
            print(f"Repository: {name}")
            print(f"Description: {description}")
            print(f"Stars: {stars}")
            print('-' * 40)
    else:
        print("No repositories found or there was an error fetching them.")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Fetch and list a GitHub user's starred repositories"
    )
    parser.add_argument("username", help="GitHub username to fetch starred repositories for")
    args = parser.parse_args(argv)

    token = os.environ.get('GITHUB_TOKEN') or None
    starred_repos = fetch_starred_repositories(args.username, token)
    display_repositories(starred_repos)
    return 0


if __name__ == "__main__":
    sys.exit(main())
