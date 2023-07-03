import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, date

def extract_content(message):
    content_type = message["content"]["content_type"]
    if content_type == "text":
        return message["content"]["parts"][0]
    elif content_type == "code":
        return message["content"]["text"]
    elif content_type == "tether_browsing_display":
        return message["content"]["result"]
    else:
        return ""

def convert_to_markdown(conversations, output_dir):
    attachments_dir = os.path.join(output_dir, "attachments")
    notes_dir = os.path.join(output_dir, "notes")

    # Create directories if they don't exist
    os.makedirs(attachments_dir, exist_ok=True)
    os.makedirs(notes_dir, exist_ok=True)

    for i, conversation in enumerate(conversations):
        title = conversation.get("title", f"conversation_{i}")
        title = title.replace("'", "")  # Remove single quotes from title
        title = title.replace(" ", "_").lower()

        conversation_id = conversation["id"]
        timestamp = datetime.fromtimestamp(conversation["create_time"])
        timestamp_str = timestamp.strftime("%Y%m%d-%H%M")
        filename = f"{timestamp_str}-{title}.md"
        conversation_path = os.path.join(notes_dir, filename)

        existing_content = ""
        if os.path.exists(conversation_path):
            with open(conversation_path, "r") as file:
                existing_content = file.read()

        with open(conversation_path, "w") as file:
            file.write("---\n")
            file.write(f"tags: [Notebooks/ChatGPT/{timestamp.strftime('%Y-%m')}]\n")
            file.write(f"title: '{conversation['title']}'\n")
            file.write(f"created: '{timestamp.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}'\n")
            file.write(f"modified: '{datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}'\n")
            file.write("---\n\n")

            file.write(f"# {conversation['title']}\n\n")

            for message_id, message_data in conversation["mapping"].items():
                message = message_data.get("message")
                if message is None:
                    continue

                role = message["author"].get("role", "")
                content = extract_content(message)

                if role == "system":
                    message_time = datetime.fromtimestamp(message["create_time"])
                    message_time_str = message_time.strftime("%Y-%m-%d %H:%M:%S")
                    file.write(f"## System ({message_time_str}):\n\n{content}\n\n")
                elif role == "user":
                    message_time = datetime.fromtimestamp(message["create_time"])
                    message_time_str = message_time.strftime("%Y-%m-%d %H:%M:%S")
                    file.write(f"{message_time_str} - User:\n```\n{content}\n```\n\n")
                elif role == "assistant":
                    message_time = datetime.fromtimestamp(message["create_time"])
                    message_time_str = message_time.strftime("%Y-%m-%d %H:%M:%S")
                    file.write(f"{message_time_str} - Assistant:\n```\n{content}\n```\n\n")

                    # Extract links visited by the assistant
                    links = message_data.get("message", {}).get("metadata", {}).get("_cite_metadata", {}).get("metadata_list", [])
                    if links:
                        file.write("Links Visited:\n")
                        for link in links:
                            title = link.get("title", "")
                            url = link.get("url", "")
                            file.write(f"- [{title}]({url})\n")

                # Handle attachments
                if "attachments" in message_data:
                    for attachment in message_data["attachments"]:
                        attachment_path = os.path.join(attachments_dir, attachment["filename"])
                        shutil.copy(attachment["path"], attachment_path)

        if existing_content != "":
            with open(conversation_path, "a") as file:
                file.write("\n")
                file.write(existing_content)

    print("Conversion to Markdown completed successfully!")



def commit_to_git(output_dir, num_conversations):
    # Get the current date in yyyy-mm-dd format
    today = date.today().strftime("%Y-%m-%d")

    # Add all Markdown files to the Git index
    subprocess.run(["git", "add", f"{output_dir}/*.md"])

    # Commit the changes with a descriptive message
    commit_message = f"Conversion of {num_conversations} conversations on {today}"
    subprocess.run(["git", "commit", "-m", commit_message])

    # Tag the commit with the current date
    subprocess.run(["git", "tag", today])

def main(input_path):
    # Check if the input path is a zip file or a directory
    if zipfile.is_zipfile(input_path):
        # Extract the zip file to a temporary directory
        temp_dir = tempfile.mkdtemp()
        with zipfile.ZipFile(input_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Get the path to conversations.json
        conversations_path = os.path.join(temp_dir, "conversations.json")
    else:
        # Assume the input path is a directory containing conversations.json
        conversations_path = os.path.join(input_path, "conversations.json")
    
    # Read conversations from conversations.json
    with open(conversations_path, "r") as file:
        conversations_data = json.load(file)
    
    # Convert conversations to markdown
    output_directory = os.path.join(os.getcwd(), "output_dir")
    convert_to_markdown(conversations_data, output_directory)
    
    # Clean up the temporary directory if it was created
    if zipfile.is_zipfile(input_path):
        shutil.rmtree(temp_dir)
    
    print("Conversion to Markdown completed successfully!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python convert-markdown.py <input_path>")
    else:
        input_path = sys.argv[1]
        main(input_path)