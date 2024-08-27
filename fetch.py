import requests
from requests.auth import HTTPBasicAuth

# Replace 'your-username' and 'your-personal-access-token' with your GitHub username and personal access token
username = 'your-username'
token = 'your-personal-access-token'

def fetch_starred_repositories(username, token):
    # GitHub API URL to fetch starred repositories
    url = f'https://api.github.com/users/{username}/starred'

    # Send a GET request to GitHub API
    response = requests.get(url, auth=HTTPBasicAuth(username, token))

    # Check if the request was successful
    if response.status_code == 200:
        return response.json()  # Return JSON response containing the repositories
    else:
        print(f"Failed to fetch starred repositories. Status code: {response.status_code}")
        return []

def display_repositories(repositories):
    # Print details of each starred repository
    if repositories:
        for repo in repositories:
            name = repo.get('name', 'No name')
            description = repo.get('description', 'No description')
            stars = repo.get('stargazers_count', 'No star count')
            print(f"Repository: {name}")
            print(f"Description: {description}")
            print(f"Stars: {stars}")
            print('-' * 40)
    else:
        print("No repositories found or there was an error fetching them.")

if __name__ == "__main__":
    starred_repos = fetch_starred_repositories(username, token)
    display_repositories(starred_repos)
