![Intro banner](intro-banner.png)

![banner](assets/banner.png)

![Animated scene](scene.svg)

# Github-Starred-Fetch

Fetches and lists the repositories a GitHub user has starred, using the GitHub API. For each starred repository it prints the name, the description (or "No description" when the repository has none), and the star count.

![Heading plate](plate.svg)

![Major separator](separator-major.svg)

## Requirements

Python 3 and the `requests` package:

```
pip install requests
```

![Heading plate](plate.svg)

![Major separator](separator-major.svg)

## How to run

```
python3 fetch.py <github-username>
```

For example:

```
python3 fetch.py octocat
```

Running with no username prints the usage message and exits 2. A
username that cannot be a GitHub username (for example one containing
a slash) is rejected with exit 2 before any request is made. A failed
request prints the reason to stderr and exits 1. Requests time out
after 15 seconds instead of waiting indefinitely.

Help:

```
python3 fetch.py --help
```

![Heading plate](plate.svg)

![Major separator](separator-major.svg)

## Authentication

No token is needed for public data, and no credential is written in the code. To raise the GitHub API rate limit or reach data your account may see, set a personal access token in the `GITHUB_TOKEN` environment variable:

```
GITHUB_TOKEN=<your token> python3 fetch.py <github-username>
```

The token is sent in the `Authorization: Bearer` header and is never printed. Do not paste a token into `fetch.py`.

![Heading plate](plate.svg)

![Major separator](separator-major.svg)

## How it works

- Requests `https://api.github.com/users/<username>/starred` with `per_page=100` and follows pages until a short page comes back, so users with more than one page of starred repositories are listed in full instead of only the first page.
- Prints one block per repository: `Repository:`, `Description:`, and `Stars:`, separated by a line of dashes.
- If the user has starred nothing, it prints "No repositories found."
  and exits 0. A failed fetch exits 1, so a script calling this one
  can tell an empty list from a failed one.
- `test_fetch.py` holds mocked tests (`python3 -m unittest`): pagination,
  the timeout, headers, bad bodies, and the exit codes. No live call
  or real token is used.

![Heading plate](plate.svg)

![Major separator](separator-major.svg)

## Files

- `fetch.py`: the script. It can also be imported: `fetch_starred_repositories(username, token=None)` returns a list of repository objects, and `display_repositories(repositories)` prints them.
- `assets/logo.png` and `assets/banner.png`: project branding.

![Heading plate](plate.svg)

![Major separator](separator-major.svg)

## License

GPL-3.0; see `LICENSE`.

![Minor separator](separator-minor.svg)

> Chalkboard note: no username prints usage and exits 2; a failed request prints its reason to stderr and exits 1.
> Chalkboard note: never paste a token into fetch.py; set GITHUB_TOKEN in the environment instead.
