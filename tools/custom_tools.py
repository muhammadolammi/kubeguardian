
import os.path as path
import os
from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#TODO this is hardly coded , get from env.
AUTHORIZED_DIRECTORY = "/home/muhammad/hackathon/kubeguardian/apps/bank-of-anthos/kubernetes-manifests"

async def get_all_manifests() -> str:
    """
    List all manifest files available in the manifests directory.
    Shows file size and whether it's a directory.
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


def get_absolute_path(name: str) -> str:
    """
    Build the absolute path for a manifest file (adds .yaml automatically).
    """
    file_name = name + ".yaml"
    return path.join(AUTHORIZED_DIRECTORY, file_name)


async def get_manifest(file_name: str) -> str:
    """
    Read and return the content of a manifest file (.yaml).
    Truncates if the file is too large.
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


