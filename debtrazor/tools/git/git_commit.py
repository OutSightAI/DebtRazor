import os
import shutil
import subprocess
import filecmp
import yaml
from github import Github, GithubException


def load_config(config_path: str) -> dict:
    """
    Load and return the configuration from a YAML file.
    """
    with open(config_path, "r") as f:
        return yaml.safe_load(f)



def copy_files_one_by_one(source_dir, dest_dir, legacy_language):
    """
    Copies files and subdirectories inside the folder matching the capitalized legacy_language
    from source_dir to dest_dir, without copying the folder itself.
    Overrides files if changes are detected.
    
    The legacy_language folder is identified, but only its contents are copied.
    """
    # Capitalize the legacy language to match folder name
    original_language = legacy_language.capitalize()

    # Path to the folder containing the legacy language
    legacy_folder_path = os.path.join(source_dir, original_language)

    # Check if the folder exists
    if not os.path.exists(legacy_folder_path) or not os.path.isdir(legacy_folder_path):
        raise FileNotFoundError(f"Folder for legacy language '{original_language}' not found in {source_dir}")

    # Walk through the legacy_language folder
    for root, dirs, files in os.walk(legacy_folder_path):
        # Determine the relative path (but without including the legacy_language folder itself)
        relative_path = os.path.relpath(root, legacy_folder_path)
        dest_root = os.path.join(dest_dir, relative_path)

        # Ensure destination subdirectory exists
        os.makedirs(dest_root, exist_ok=True)

        # Copy each file individually
        for file in files:
            source_file = os.path.join(root, file)
            dest_file = os.path.join(dest_root, file)  # The file name stays the same

            # If file doesn't exist at the destination, copy it
            if not os.path.exists(dest_file):
                shutil.copy2(source_file, dest_file)
                print(f"Copied new file: {source_file} -> {dest_file}")
            else:
                # If the file exists, check if the contents are different
                if not filecmp.cmp(source_file, dest_file, shallow=False):
                    shutil.copy2(source_file, dest_file)  # Override the file
                    print(f"Overridden file: {source_file} -> {dest_file}")
                else:
                    print(f"File already exists and is unchanged: {dest_file}")


def push_changes_to_github(cfg):
    """
    Push changes to the specified GitHub repo and branch using PyGithub and subprocess for Git commands.
    """

    try:
        # Authenticate using PyGithub and get the repo object
        g = Github(cfg.github_token)

        print(g)
        print(f"{cfg.github_username}/{cfg.repo_name}")

        g.get_repo(f"{cfg.github_username}/{cfg.repo_name}")

        # Copy files from source directory to destination one by one
        copy_files_one_by_one(cfg.output_path, cfg.entry_path, cfg.legacy_language)

        # Path to the local repository (destination directory)
        repo_path = cfg.entry_path


        # Ensure the branch exists locally, create it if it doesn't
        try:
            subprocess.run(["git", "rev-parse", "--verify", cfg.git_branch], cwd=repo_path, check=True)
        except subprocess.CalledProcessError:
            # If branch does not exist locally, create it
            subprocess.run(["git", "checkout", "-b", cfg.git_branch], cwd=repo_path, check=True)

        # Set up the Git remote with token authentication
        remote_url = f"https://{cfg.github_username}:{cfg.github_token}@github.com/{cfg.github_username}/{cfg.repo_name}.git"
        subprocess.run(["git", "remote", "set-url", "origin", remote_url], cwd=repo_path, check=True)

        # Check the remote URL to ensure it's properly set
        subprocess.run(["git", "remote", "-v"], cwd=repo_path, check=True)

        # Stage all changes
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True)

        # Commit the changes
        subprocess.run(["git", "commit", "-m", cfg.commit_message], cwd=repo_path, check=True)

        # Push the changes to the remote and set upstream branch for future pushes
        subprocess.run(["git", "push", "--set-upstream", "origin", cfg.git_branch], cwd=repo_path, check=True)

        print("Changes pushed successfully")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        raise RuntimeError(f"Git command failed: {str(e)}")

    except GithubException as e:
        raise RuntimeError(f"GitHub API error: {str(e)}")

    except Exception as e:
        raise RuntimeError(f"An unexpected error occurred: {str(e)}")

