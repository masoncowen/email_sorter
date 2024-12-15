# Outlook Wrapper to categorise and sort emails
This is a little GUI tool, still very much WIP.

Declare `$PY_OUTLOOK_SORTER_PATH` in your configs or otherwise store the config in `$XDF_CONFIG_HOME/pyOutlookSorter/config.json`

A minimum example config is as below, I'll update and improve the readme once the program is more complete:

```
{
    "outlook": {
        "account": "Outlook Account",
        "folder": "Inbox",
        "archive": "Archive"
    },
    "tabs": [
        {
            "name": "All"
        }
    ],
    "categories": [
        {
            "text": "Bounce-back Message",
            "jobs": [
                "EmailDefault",
                "ArchiveEmail"
            ]
            "new_types": [
                "Bounce-back"
            ]
        },
        {
            "text": "Fetch information",
            "jobs": [
                "EmailDefault"
                ],
            "new_types": [
                "Request: Information"
                ],
            "new_actions": [
                "Fetch Information"
                ]
        }
    ],
    "actions": [
        {
            "text": "Initial Categorisation",
            "command": "initial_categorise"
        },
        {
            "text": "Fetch Information",
            "command": "shell command-line"
        }
    ]
}
```
