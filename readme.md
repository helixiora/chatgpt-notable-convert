# ChatGPT Data Export to Notable App Directory Converter

This script converts a ChatGPT data export to a Notable app directory structure, allowing you to import your conversations into Notable for better organization and note-taking.

## Overview

This script converts the ChatGPT data export, which is a JSON file containing conversation data, into a directory structure compatible with the Notable app. The converter generates Markdown files for each conversation, along with attachments if available.

For more information on exporting ChatGPT data, refer to the OpenAI documentation: [How do I export my ChatGPT history and data?](https://help.openai.com/en/articles/7260999-how-do-i-export-my-chatgpt-history-and-data)

## Usage

1. Install the required dependencies by running:
   ```
   pip install -r requirements.txt
   ```

2. Run the script with the following command:

   For a ChatGPT data export JSON file:
   ```
   python convert-to-notable.py path/to/chatgpt_export.json
   ```

   Note: The `TMPDIR` environment variable, if set, will be used as the temporary directory for extracting zip files.

3. The script will generate the Notable app directory structure in the `output_dir` directory.

## Output Directory Structure

The output directory will have the following structure:

```
output_dir/
├── attachments/
│   ├── attachment_1.ext
│   ├── attachment_2.ext
│   └── ...
└── notes/
    ├── conversation_1.md
    ├── conversation_2.md
    └── ...
```

The `attachments` directory will contain any attachment files associated with the conversations, and the `notes` directory will contain the generated Markdown files for each conversation.

## Customization

- To modify the format of the generated Markdown files, you can edit the `convert_to_notable` function in the `convert-to-notable.py` script.

- Feel free to customize the script according to your specific requirements.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
