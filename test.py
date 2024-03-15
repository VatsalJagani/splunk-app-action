
import os

def create_file_with_permissions(filepath, content="", mode=0o644):
  """
  Creates a file with the specified path, content, and permissions.

  Args:
      filepath (str): The path to the file to create.
      content (str, optional): The content to write to the file. Defaults to "".
      mode (int, optional): The octal representation of the desired file permissions. Defaults to 0o644 (read-only for user and group, read-only for others).
  """
  # Ensure directory exists (optional)
#   os.makedirs(os.path.dirname(filepath), exist_ok=True)  # Create directories if needed

  try:
    with open(filepath, "w") as f:
      f.write(content)  # Write content if provided
    # Set file permissions using os.chmod
    os.chmod(filepath, mode)
    print(f"File created successfully: {filepath}")
  except OSError as e:
    print(f"Error creating file: {e}")

# Example usage
file_path = "file1.sh"
content = "This file is executable before hand."
permissions = 0o755  # Read, write, and execute for owner, read and execute for group, read and execute for others

# file_path = "file2.sh"
# content = "This file is not executable but needs to be executable."
# permissions = 0o644  # Read, write, and execute for owner, read and execute for group, read-only for others

# file_path = "file3.txt"
# content = "This file is executable but should not be executable."
# permissions = 0o755  # Read, write, and execute for owner, read and execute for group, read and execute for others

# file_path = "file4.txt"
# content = "This file is not executable and this is how it should be."
# permissions = 0o644  # Read, write, and execute for owner, read and execute for group, read-only for others


create_file_with_permissions(file_path, content, permissions)
