import fnmatch
import os
import re
from pathlib import Path


def parse_gitignore(directory):
    gitignore_patterns = []
    gitignore_path = os.path.join(directory, ".gitignore")
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as gitignore_file:
            for line in gitignore_file:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Convert gitignore pattern to regex
                    pattern = line.replace(".", r"\.")
                    pattern = pattern.replace("*", ".*")
                    pattern = pattern.replace("?", ".")
                    if pattern.startswith("**/"):
                        pattern = pattern[3:]
                    if pattern.startswith("/"):
                        pattern = "^" + pattern[1:]
                    else:
                        pattern = "/" + pattern
                    if pattern.endswith("/"):
                        pattern += ".*"
                    gitignore_patterns.append(re.compile(pattern))
    return gitignore_patterns


def should_ignore(path, base_path, ignore_patterns):
    rel_path = "/" + os.path.relpath(path, base_path).replace("\\", "/")
    for pattern in ignore_patterns:
        if pattern.search(rel_path):
            return True
    return False


def get_code_files(directory, patterns, ignore_patterns):
    for root, dirs, files in os.walk(directory):
        # Remove ignored directories
        dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d), directory, ignore_patterns)]

        for pattern in patterns:
            for filename in fnmatch.filter(files, pattern):
                file_path = os.path.join(root, filename)
                if not should_ignore(file_path, directory, ignore_patterns):
                    yield file_path


def create_output_file(directory, output_file, patterns):
    ignore_patterns = parse_gitignore(directory)
    with open(output_file, "w", encoding="utf-8") as outfile:
        for file_path in get_code_files(directory, patterns, ignore_patterns):
            relative_path = os.path.relpath(file_path, directory)
            outfile.write(f"[# {relative_path}]\n")

            try:
                with open(file_path, "r", encoding="utf-8") as infile:
                    content = infile.read()
                    outfile.write(content)
            except UnicodeDecodeError:
                outfile.write("Unable to read file: encoding issue\n")
            except Exception as e:
                outfile.write(f"Error reading file: {str(e)}\n")

            outfile.write("\n\n")


if __name__ == "__main__":
    # Directory to search for code files
    search_directory = "."  # Current directory, change this if needed

    # Output file name
    output_file = "code_contents.txt"

    # Patterns for code files (add or remove as needed)
    code_patterns = ["*.py", "*.js", "*.jsx", "*.html", "*.css", "*.java", "*.cpp", "*.h", "package.json"]

    create_output_file(search_directory, output_file, code_patterns)
    print(f"Output file '{output_file}' has been created.")
