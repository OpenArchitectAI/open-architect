import difflib
from github import InputGitTreeElement


def generate_diffs(previous_files, updated_files):
    diffs = {}

    # Iterate over the updated files
    for file_path, updated_content in updated_files.items():
        # Check if the file exists in the previous files
        if file_path in previous_files:
            previous_content = previous_files[file_path]

            # Generate the diff using difflib
            diff = difflib.unified_diff(
                previous_content.splitlines(keepends=True),
                updated_content.splitlines(keepends=True),
                fromfile=file_path,
                tofile=file_path,
                lineterm="\n",
            )

            # Join the diff lines into a single string
            diff_string = "".join(diff)

            # Add the diff to the diffs dictionary if it's not empty
            if diff_string:
                diffs[file_path] = f"--- {file_path}\n+++ {file_path}\n{diff_string}"
        else:
            # If the file is new, add it to the diffs dictionary with the entire content as the diff
            diffs[file_path] = f"--- /dev/null\n+++ {file_path}\n" + "\n".join(
                [f"+{line}" for line in updated_content.splitlines(keepends=True)]
            )

    return diffs


def create_modified_files(repo, diffs):
    modified_files = []
    for file_path, diff in diffs.items():
        diff_block = f"diff --git a/{file_path} b/{file_path}\n{diff}"
        lines = diff_block.strip().split("\n")
        blob_content = "\n".join(lines[5:])
        blob = repo.create_git_blob(blob_content, "utf-8")
        modified_files.append(
            InputGitTreeElement(
                path=file_path, mode="100644", type="blob", sha=blob.sha
            )
        )
    return modified_files


# # Example usage
# previous_files = {
#     "file1.txt": "Line 1\nLine 2\nLine 3\n",
#     "file2.txt": "Hello, World!\n",
# }

# updated_files = {
#     "file1.txt": "Line 1\nLine 2 - Updated\nLine 3\nLine 4\n",
#     "file2.txt": "Hello, World!\nAdditional line\n",
#     "file3.txt": "This is a new file.\n",
# }

# diffs = generate_diffs(previous_files, updated_files)

# Create the modified_files list using the diffs dictionary
# # modified_files = create_modified_files(repo, diffs)
