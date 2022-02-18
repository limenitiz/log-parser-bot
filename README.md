### How to add bot on server
[Add bot on server](https://buttery-quill-d43.notion.site/Create-discord-bot-manual-1de9e5b6b62e4547926a74f7247d9bc1)

### The server where the bot was tested
[Server](https://discord.gg/ufQFNwgx)

### Requirements for run
#### For run bot you must have .env file

    # .env 
    DISCORD_TOKEN=

#### Dependencies
    pip install discord.py
>
    pip install python-decouple

#### Run
    python main.py

### Command examples
---
    --get-visitors-channel-datetime Общий "2022-02-10 00:00" "2022-02-17 23:59"
>
    --get-1 Общий "2022-02-10 00:00" "2022-02-17 23:59"
--- 
    --get-visitors-channel-today Общий
>
    --get-2 Основной
---
    --get-visitors-channel-day Общий 17
>
    --get-3 Общий 17
---

