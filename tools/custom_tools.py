
import os.path as path
import os
from typing import Optional



cwd = os.getcwd()

def get_devs_name()-> str:
    """"
    Get the project developers name.

    Args:
    Returns:
       The developer name 
    """
    return("Dev Name is Muhammad Akewukanwo")




class filesystem():
    """
    File system utility restricted to a given directory (default: ./apps).
    """

    def __init__(self, files_directory: Optional[str] = None):
        cwd = os.getcwd()
        if files_directory is None:
            files_directory = path.join(cwd, "apps")

        if not path.isabs(files_directory):
            files_directory = path.abspath(path.expanduser(path.join(cwd, files_directory)))

        self.files_directory = files_directory

    def _isinsidefilesDirectory(self, file_path: str) -> bool:
        return path.commonpath([self.files_directory]) == path.commonpath([self.files_directory, file_path])
    
    def _resolve_dir(self,  directory):
            """
    Resolve a directory path relative to self.files_directory into an absolute path.
    """
            if not os.path.isabs(directory):
                    directory = path.abspath(path.expanduser(path.join(self.files_directory, directory)))

            return  directory 

    def get_files_info(self, directory: Optional[str] = None) -> str:
        """
        List files in a directory and basic info.
        """
        if directory is None:
            directory = self.files_directory
        directory = self._resolve_dir(directory)  

        try:
            if not self._isinsidefilesDirectory(directory):
                return f'Error: "{directory}" is outside the working directory'

            if not path.isdir(directory):
                return f'Error: "{directory}" is not a directory'

            file_contents = os.listdir(directory)
            files_infos = {}
            for content in file_contents:
                content_full_path = path.join(directory, content)
                file_size = path.getsize(content_full_path)
                is_dir = path.isdir(content_full_path)
                files_infos[content] = {
                    "file_size": file_size,
                    "is_dir": is_dir,
                }

            return "\n".join(
                [f"{c}: file_size={files_infos[c]['file_size']} bytes, is_dir={files_infos[c]['is_dir']}" for c in file_contents]
            )

        except Exception as e:
            return f"Error: {e}"



    def get_file_content(self, file_path: str) -> str:

        """
        Read the content of a file (up to 10,000 chars).
        """
        try:
            file_path = self._resolve_dir(file_path)
            if not self._isinsidefilesDirectory(file_path):
                return f'Error: Cannot read "{file_path}" as it is outside the permitted files directory'

            if not os.path.isfile(file_path):
                return f'Error: File not found or is not a regular file: "{file_path}"'

            with open(file_path, "r") as f:
                output = f.read()

            if len(output) > 10000:
                output = output[:10000] + f' [...File "{file_path}" truncated at 10000 characters]'
            return output
        except Exception as e:
            return f'Error: {e}'
        

    def get_absolute_path(self, relative_path: str) -> str:
        """
        Resolve a given path into an absolute path inside the permitted directory.

        Args:
            relative_path (str): The relative or absolute path provided by the user.

        Returns:
            str: The safe absolute path, or an error message if outside permitted directory.
        """
        try:
            # Resolve path relative to files_directory
            abs_path = self._resolve_dir(relative_path)

            # Check security boundary
            if not self._isinsidefilesDirectory(abs_path):
                return f'Error: "{relative_path}" resolves outside the permitted directory'

            return abs_path
        except Exception as e:
            return f"Error: {e}"
