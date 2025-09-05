
import os.path as path
import os
from typing import Optional



cwd = os.getcwd()
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_mail(smtp_server: str, smtp_port: int, username: str, password: str, sender: str, recipient: str, title: str, body: str):
    """
    Send an email with the given title and body.

    Args:
        smtp_server (str): SMTP server address (e.g., "smtp.gmail.com").
        smtp_port (int): SMTP server port (e.g., 587 for TLS).
        username (str): SMTP username (usually your email).
        password (str): SMTP password or app-specific password.
        sender (str): From email address.
        recipient (str): To email address.
        title (str): Email subject.
        body (str): Email body (plain text).
    """
    try:
        # Create email container
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = recipient
        msg["Subject"] = title

        # Attach body as plain text
        msg.attach(MIMEText(body, "plain"))

        # Send mail
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure connection
            server.login(username, password)
            server.sendmail(sender, recipient, msg.as_string())

        print(f"✅ Email sent to {recipient}: {title}")

    except Exception as e:
        print(f"❌ Failed to send email: {e}")


def get_devs_name()-> str:
    """"
    Get the project developers name.

    Args:
    Returns:
       The developer name 
    """
    return("Dev Name is Muhammad Akewukanwo")




# class filesystem():
#     """
#     File system utility restricted to a given directory (default: ./apps).
#     """

#     def __init__(self, files_directory: str):
#         self.files_directory = files_directory

#     def _isinsidefilesDirectory(self, file_path: str) -> bool:
#         return path.commonpath([self.files_directory]) == path.commonpath([self.files_directory, file_path])
    
#     def _resolve_dir(self,  directory):
#         """
#     Resolve a directory path relative to self.files_directory into an absolute path.
#     """
#         if not os.path.isabs(directory):
#             directory = path.abspath(path.expanduser(path.join(self.files_directory, directory)))

#         return  directory 

#     async def get_files_info(self, directory: Optional[str] = None) -> str:
#         """
#         List files in a directory and basic info.
#         """
#         if directory is None:
#             directory = self.files_directory
#         directory = self._resolve_dir(directory)  

#         try:
#             if not self._isinsidefilesDirectory(directory):
#                 return f'Error: "{directory}" is outside the working directory'

#             if not path.isdir(directory):
#                 return f'Error: "{directory}" is not a directory'

#             file_contents = os.listdir(directory)
#             files_infos = {}
#             for content in file_contents:
#                 content_full_path = path.join(directory, content)
#                 file_size = path.getsize(content_full_path)
#                 is_dir = path.isdir(content_full_path)
#                 files_infos[content] = {
#                     "file_size": file_size,
#                     "is_dir": is_dir,
#                 }

#             return "\n".join(
#                 [f"{c}: file_size={files_infos[c]['file_size']} bytes, is_dir={files_infos[c]['is_dir']}" for c in file_contents]
#             )

#         except Exception as e:
#             return f"Error: {e}"



#     async def get_file_content(self, file_path: str) -> str:

#         """
#         Read the content of a file (up to 10,000 chars).
#         """
#         try:
#             file_path = self._resolve_dir(file_path)
#             if not self._isinsidefilesDirectory(file_path):
#                 return f'Error: Cannot read "{file_path}" as it is outside the permitted files directory'

#             if not os.path.isfile(file_path):
#                 return f'Error: File not found or is not a regular file: "{file_path}"'

#             with open(file_path, "r") as f:
#                 output = f.read()

#             if len(output) > 10000:
#                 output = output[:10000] + f' [...File "{file_path}" truncated at 10000 characters]'
#             return output
#         except Exception as e:
#             return f'Error: {e}'
        

#     def get_absolute_path(self, relative_path: str) -> str:
#         """
#         Resolve a given path into an absolute path inside the permitted directory.

#         Args:
#             relative_path (str): The relative or absolute path provided by the user.

#         Returns:
#             str: The safe absolute path, or an error message if outside permitted directory.
#         """
#         try:
#             # Resolve path relative to files_directory
#             abs_path = self._resolve_dir(relative_path)

#             # Check security boundary
#             if not self._isinsidefilesDirectory(abs_path):
#                 return f'Error: "{relative_path}" resolves outside the permitted directory'

#             return abs_path
#         except Exception as e:
#             return f"Error: {e}"


import os
from os import path
from typing import Optional



    

def is_inside_files_directory(files_directory, file_path: str) -> bool:
    """
    Check whether a given path stays inside the base files_directory.
    """
    return path.commonpath([files_directory]) == path.commonpath(
        [files_directory, file_path]
    )

def resolve_dir(files_directory:str, directory: str) -> str:
    """
    Resolve a directory path relative to self.files_directory into an absolute path.
    """
    if not path.isabs(directory):
        directory = path.abspath(path.join(files_directory, directory))
    else:
        # Normalize absolute paths too
        directory = path.abspath(directory)

    return directory

        

async def get_files_info(files_directory:str, directory: Optional[str] = None) -> str:
    """
    List files in a directory with basic info.
    """
    if directory is None:
        directory = files_directory
    directory = resolve_dir(files_directory, directory)

    try:
        if not is_inside_files_directory(directory):
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
            [
                f"{c}: file_size={files_infos[c]['file_size']} bytes, "
                f"is_dir={files_infos[c]['is_dir']}"
                for c in file_contents
            ]
        )

    except Exception as e:
        return f"Error: {e}"

async def get_file_content(files_directory:str, file_path: str) -> str:
    """
    Read the content of a file (up to 10,000 chars).
    """
    try:
        file_path = resolve_dir(files_directory,file_path)

        if not is_inside_files_directory(files_directory, file_path):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted files directory {files_directory}'

        if not path.isfile(file_path):
            return f'Error: File not found or not a regular file: "{file_path}"'

        with open(file_path, "r", encoding="utf-8") as f:
            output = f.read()

        if len(output) > 10000:
            output = (
                output[:10000]
                + f' [...File "{file_path}" truncated at 10000 characters]'
            )
        return output
    except Exception as e:
        return f"Error: {e}"

def get_absolute_path(files_directory:str, relative_path: str) -> str:
    """
    Resolve a given path into an absolute path inside the permitted directory.
    """
    try:
        abs_path = resolve_dir(files_directory, relative_path)

        if not is_inside_files_directory(abs_path):
            return f'Error: "{relative_path}" resolves outside the permitted directory'

        return abs_path
    except Exception as e:
        return f"Error: {e}"
