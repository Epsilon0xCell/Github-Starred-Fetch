![banner](assets/banner.png)

# Github-Starred-Fetch

Fetches and lists the repositories a GitHub user has starred, using the GitHub API. For each starred repository it prints the name, the description (or "No description" when the repository has none), and the star count.

## Requirements

Python 3 and the `requests` package:

```
pip install requests
```

## How to run

```
python3 fetch.py <github-username>
```

For example:

```
python3 fetch.py octocat
```

Running with no username, or with an unknown username, is handled without a traceback: a missing username prints the usage message, and a failed request prints the HTTP status code. Network errors are reported the same way.

Help:

```
python3 fetch.py --help
```

## Authentication

No token is needed for public data, and no credential is written in the code. To raise the GitHub API rate limit or reach data your account may see, set a personal access token in the `GITHUB_TOKEN` environment variable:

```
GITHUB_TOKEN=<your token> python3 fetch.py <github-username>
```

The token is sent in the `Authorization: Bearer` header and is never printed. Do not paste a token into `fetch.py`.

## How it works

- Requests `https://api.github.com/users/<username>/starred` with `per_page=100` and follows pages until a short page comes back, so users with more than one page of starred repositories are listed in full instead of only the first page.
- Prints one block per repository: `Repository:`, `Description:`, and `Stars:`, separated by a line of dashes.
- If nothing is found, or the request fails, it prints "No repositories found or there was an error fetching them." after any status message.

## Files

- `fetch.py`: the script. It can also be imported: `fetch_starred_repositories(username, token=None)` returns a list of repository objects, and `display_repositories(repositories)` prints them.
- `assets/logo.png` and `assets/banner.png`: project branding.

## License

GPL-3.0; see `LICENSE`.
