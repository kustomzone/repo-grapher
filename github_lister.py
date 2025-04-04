
"""

  <name> Github Repo Lister </name>
	<produced>     Kustomzone     </produced>
	<author>       Gemini2.5      </author>
	<version>      0.0.1          </version>

  <function> Get Github repos by user and language </finction>
  <status>   Username and language currently used as filters for repo list output.txt </status>
  <tokens>   Limited to Github's daily allotment of public API calls (60?) with max 100 repos per page </tokens>

"""

import requests
import json

def get_github_repos(username):
    """
    Fetches all public repositories for a given GitHub username.
    Handles pagination to retrieve all repositories.
    """
    repos = []
    page = 1
    per_page = 100  # Max allowed by GitHub API
    api_url_base = f"https://api.github.com/users/{username}/repos"

    print(f"Fetching repositories for user '{username}'...")

    while True:
        # Construct the URL for the current page
        api_url = f"{api_url_base}?page={page}&per_page={per_page}"
        try:
            # Make the GET request to the GitHub API
            response = requests.get(api_url)
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status()

            # Parse the JSON response
            current_page_repos = response.json()

            # If the current page is empty, we've fetched all repos
            if not current_page_repos:
                break

            # Add the fetched repos to our list
            repos.extend(current_page_repos)
            print(f"Fetched page {page} ({len(current_page_repos)} repos)")

            # Move to the next page
            page += 1

        except requests.exceptions.RequestException as e:
            print(f"Error fetching repositories: {e}")
            # Check for specific status codes if needed
            if response.status_code == 404:
                print(f"Error: GitHub user '{username}' not found.")
            elif response.status_code == 403:
                print("Error: GitHub API rate limit likely exceeded. Try again later or use authentication.")
            return None # Indicate failure

    print(f"Finished fetching. Total repositories found: {len(repos)}")
    return repos

def filter_and_save_repos(repos, language_filter, output_filename="output.txt"):
    """
    Filters repositories by language and saves them to a file.
    """
    if repos is None:
        print("No repositories to filter.")
        return

    # Convert the filter to lowercase for case-insensitive comparison
    language_filter_lower = language_filter.lower()
    filtered_repos = []

    print(f"Filtering repositories by language: '{language_filter}'...")

    for repo in repos:
        # Check if the 'language' key exists and is not None
        if repo.get('language') and repo['language'].lower() == language_filter_lower:
            filtered_repos.append(repo)

    print(f"Found {len(filtered_repos)} repositories matching the language filter.")

    # Write the filtered repositories to the output file
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            count = 1
            for repo in filtered_repos:
                # Ensure description is not None before writing
                description = repo.get('description', 'No description provided.')
                if description is None:
                    description = 'No description provided.'

                f.write(f"{count}. Name:         {repo['name']}\n")
                f.write(f"   Description:  {description}\n")
                f.write(f"   URL:          {repo['html_url']}\n")
                f.write(f"   Last Push:    {repo['pushed_at']}\n")
                f.write(f"   Language:     {repo['language']}\n")
                f.write("---------------\n")
                count += 1
        print(f"Successfully wrote filtered repositories to '{output_filename}'")
    except IOError as e:
        print(f"Error writing to file '{output_filename}': {e}")

# --- Main execution ---
if __name__ == "__main__":
    github_username = input("Enter your GitHub username: ")
    language = input("Enter the programming language to filter by (e.g., Python, JavaScript): ")

    if github_username and language:
        all_repos = get_github_repos(github_username)
        if all_repos: # Only proceed if fetching was successful
            filter_and_save_repos(all_repos, language)
    else:
        print("Username and language cannot be empty.")

