from const import get_ENV
from helpers import AlertDB
import os.path as path
import os

AUTHORIZED_DIRECTORY = get_ENV("AUTHORIZED_DIRECTORY")
DB_URL = get_ENV("DB_URL")
CRYPT_KEY = get_ENV("CRYPT_KEY")
alertdb = AlertDB(db_url=DB_URL, crypt_key=CRYPT_KEY)







async def get_all_manifests(n:str) -> str:
    """
    List all manifest files available in the manifests directory. Shows file size and whether it's a directory.
    Args:
        n (str) : An empty unused string

    Returns
        str: all manifest files and info in authorized namespace        
    """
    try:
        if not path.isdir(AUTHORIZED_DIRECTORY):
            return f'Error: "{AUTHORIZED_DIRECTORY}" is not a directory'

        file_contents = os.listdir(AUTHORIZED_DIRECTORY) 
        files_infos = {}
        for content in file_contents:
            content_full_path = path.join(AUTHORIZED_DIRECTORY, content)
            file_size = path.getsize(content_full_path)
            is_dir = path.isdir(content_full_path)
            files_infos[content] = {
                "file_size": file_size,
                "is_dir": is_dir,
            }

        return "\n".join(
            f"{c}: file_size={files_infos[c]['file_size']} bytes, "
            f"is_dir={files_infos[c]['is_dir']}"
            for c in file_contents
        )

    except Exception as e:
        return f"Error: {e}"


def get_absolute_path(file_name: str) -> str:
    """
    Build the absolute path for a manifest file.
    Args:
        file_name(str) : filename to get it absolute ending in .yaml eg (mcp-server.yaml)
    Returns:
        str: absolute path resolved to the authorized directory
    """
    return path.join(AUTHORIZED_DIRECTORY, file_name)
 

async def get_manifest(file_name: str) -> str:
    """
    Read and return the content of a manifest file (.yaml). Truncates if the file is too large.
    Args:
        file_name(str) : The file name for the manifest ending in .yaml
    Returns:
        str: file content (truncated if too large)
   
    """
    try:
        file_path = get_absolute_path(file_name)
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



def get_devs_name(n:str)-> str: 
    """"
    Get the project developers name.
    Args:
        n (str) : An empty unused string
    Returns:
       str: The developer name 
       
    """
    return("Dev Name is Muhammad Akewukanwo")

def create_alert(body:str, session_id:str, severity:str):
    """"
    Send an email with the given title and body.
    Args:
        body (str): alert body 
        severity(str): severity of alert
        session_id(str): current session body

    Returns:
        str: Sucess/Failure depending on send result
    """
    try:
        alertdb.update_alert(body=body, session_id=session_id, severity=severity)
        return "Alert sent"
    except Exception as e:
        return f"Error sending alert. Error: {e}"





# def create_title( title:str, tool_context: ToolContext):
#     """
#         Update Session title in state if not available. 
        
#         Args:
#             title (str): Title value to set in state.

#         Returns:
#             str: Success or failure message.
#         """
#     try:
#         v = tool_context.state.get("session_title")
#         if v==value:
#             return "Old value same as new, no update"
#         if v:
#             return "There's already a title, no update"
#         if not v:
#            tool_context.state["session_title"]=value
#            return "Success creating state."
       
        

#     except Exception as e:
#         logger.exception(f"Error updating state: {e}")
#         return f"Failure to update state. Error: {e}"
    

