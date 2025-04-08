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
    headers = {'Accept': 'application/vnd.github.v3+json'} # Recommended header

    print(f"Fetching repositories for user '{username}'...")

    while True:
        # Construct the URL for the current page
        api_url = f"{api_url_base}?page={page}&per_page={per_page}"
        response = None # Initialize response to None for error handling scope
        try:
            # Make the GET request to the GitHub API
            response = requests.get(api_url, headers=headers)
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
            if response is not None: # Check if response object exists
                 if response.status_code == 404:
                    print(f"Error: GitHub user '{username}' not found.")
                 elif response.status_code == 403:
                    # Check for rate limit headers
                    rate_limit_info = response.headers.get('X-RateLimit-Remaining')
                    if rate_limit_info == '0':
                        print("Error: GitHub API rate limit exceeded. Try again later or use authentication.")
                    else:
                        print("Error: Access forbidden. Check credentials or permissions if using authentication.")
            return None # Indicate failure

    print(f"Finished fetching. Total repositories found: {len(repos)}")
    return repos

def filter_and_save_repos(repos, language_filter, include_size, sort_by_size, output_filename="output.txt"):
    """
    Filters repositories by language (optional), sorts them based on user preference,
    and saves them to a file.
    """
    if repos is None:
        print("No repositories to filter.")
        return

    # --- Filtering ---
    if language_filter:
        # Filter by language (case-insensitive)
        language_filter_lower = language_filter.lower()
        filtered_repos = [
            repo for repo in repos
            if repo.get('language') and repo['language'].lower() == language_filter_lower
        ]
        print(f"Filtering by language: '{language_filter}'. Found {len(filtered_repos)} matching repositories.")
    else:
        # No language filter, include all repositories
        filtered_repos = list(repos) # Create a copy
        print("No language filter applied. Including all repositories.")

    # --- Sorting ---
    if sort_by_size:
        print("Sorting repositories by size (largest first)...")
        # Sort by 'size' (descending). The 'size' field is in KB.
        filtered_repos.sort(key=lambda repo: repo.get('size', 0), reverse=True)
    elif not language_filter:
        print("Sorting repositories by language (alphabetical)...")
        # Sort by language (alphabetical, None values last)
        filtered_repos.sort(key=lambda repo: (repo.get('language') is None, str(repo.get('language', '')).lower()))
    else:
        # Default sort order (usually by name from API) when filtering by language but not size
        print("Keeping default repository order (filtered by language).")


    # --- Writing to File ---
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            count = 1
            for repo in filtered_repos:
                # Ensure description is not None before writing
                description = repo.get('description', 'No description provided.')
                if description is None: # Handle explicitly None descriptions
                    description = 'No description provided.'

                # Get language, handle None
                language = repo.get('language', 'N/A') # Use N/A if language is None

                f.write(f"{count}. Name:         {repo['name']}\n")
                f.write(f"   Description:  {description}\n")
                f.write(f"   URL:          {repo['html_url']}\n")
                f.write(f"   Last Push:    {repo['pushed_at']}\n")
                f.write(f"   Language:     {language}\n")
                if include_size:
                    f.write(f"   Size (KB):    {repo.get('size', 'N/A')}\n") # Add size if requested
                f.write("---------------\n")
                count += 1
        print(f"Successfully wrote {len(filtered_repos)} repositories to '{output_filename}'")
    except IOError as e:
        print(f"Error writing to file '{output_filename}': {e}")

# --- Main execution ---
if __name__ == "__main__":
    github_username = input("Enter your GitHub username: ")

    # Only proceed if username is provided
    if not github_username:
        print("Username cannot be empty.")
    else:
        # Get language filter (allow empty input)
        language = input("Enter language to filter by (leave blank for all languages): ")

        # Ask about including size and sorting
        include_size_input = input("Include repo sizes and sort by largest first? (y/n): ").lower()
        should_include_size = include_size_input == 'y'
        should_sort_by_size = include_size_input == 'y' # Sorting by size is tied to including it in this prompt

        # Fetch repositories
        all_repos = get_github_repos(github_username)

        # Filter and save if fetching was successful
        if all_repos:
            filter_and_save_repos(
                repos=all_repos,
                language_filter=language.strip(), # Use stripped language input
                include_size=should_include_size,
                sort_by_size=should_sort_by_size,
                output_filename="output.txt" # Explicitly pass filename
            )

