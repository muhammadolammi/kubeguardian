
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
    """"
    Get the project developers name.

    Args:
       files_folder: the absolute path to the folder we want the ai to access, it wont access any file outside of this.
                      default will be the cwd/app , the idea is that the agent should take care of the apps not the core codes of the agent.
                      cwd= os.getcwd()
                      if relative it will be relative to cwd 
    Returns:
       The developer name 
    """
    def __init__(self, files_directory: Optional[str] = None):
        cwd = os.getcwd()
        if files_directory is None:
            files_directory = f"{cwd}/app"
        # if a relative directory was provided
        if not os.path.isabs(files_directory):
            main_dir = cwd
            # Resolve relative path to cwd to get absolute path.
            files_directory = path.abspath(path.expanduser(path.join(main_dir, files_directory)))
        self.files_directory = files_directory

    def _isinsidefilesDirectory(self, file_path:str):
        if  path.commonpath([self.files_directory]) == path.commonpath([self.files_directory, file_path]):
                return True 
        return False

    def get_files_info(self, directory:str):
        """
        Return list of files in a directory.

        Args:
            directory (str): Absolute path to the directory.
        """
        try:
            
            # directory =  self._resolve_current_dir( directory)
            
            if not self._isinsidefilesDirectory(directory):
                # print(f'Error: "{directory}" is outside the working directory')
                return f'Error: "{directory}" is outside the working directory'

            # if not path.exists(directory):
            #     # print(f'Error: "{directory}" does not exist')
            #     return f'Error: "{directory}" does not exist'

            if not path.isdir(directory):
                # print(f'Error: "{directory}" is not a directory')
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

            return_str = "\n"
            for content in file_contents:
                result = f"{content}: file_size={files_infos[content]['file_size']} bytes, is_dir={files_infos[content]['is_dir']}\n"
                return_str += result
            return return_str

        except Exception as e:
            return f"Error: {e}" 
    
    def get_file_content(self, file_path: str) -> str:
        """
        Get content of a file.

        Args:
            file_path (str): Absolute path to the file.
        """
        try:
            if not self._isinsidefilesDirectory( file_path):
                return f'Error: Cannot read "{file_path}" as it is outside the permitted files directory'
            if not os.path.isfile(file_path):
                return f'Error: File not found or is not a regular file: "{file_path}"'
            output = ""
            with open(file_path, "r") as f:
                output = f.read()
            # The target is likely yaml files , but we need the truncating to avoid using memory , incase.
            if len(output)>10000:
                output = output[:10000] + f' [...File "{file_path}" truncated at 10000 characters]'

            return output
        except Exception as e:
            return f'Error: {e}'


