 <h1 align=center> 
  Undermine Goblin
 </h1>

<h4 align="center"> WIP</h4>

GIF here

## Table of Contents

- [Key Features](#-key-features)
- [Requirements & Prerequisites](#️-requirements--prerequisites)
- [Installation](#️-installation)
- [Usage](#️-usage)
- [Roadmap](#️-roadmap)
- [Licence](#-licence)

## 🚀 Key Features

- Built on Django to provide robust data management and task handling.
- Discord bot for managing tracked items.
- Scrape item prices from Undermine.exchange hourly and deliver them via the bot.
- Create price graphs.


## 🛠️ Requirements & Prerequisites

- **[uv](https://docs.astral.sh/uv/)** An extremely fast Python package and project manager
- **Python** version 3.14 or higher
- **Chromium executable** for Playwright
- **Discord bot** [How to create one](https://docs.discord.com/developers/quick-start/getting-started#step-1-creating-an-app)

## ⚙️ Installation

1. Clone the repository:
```bash
git clone https://github.com/Darnikus/undermine-goblin

cd undermine-goblin
```

2. Install dependencies and set up the enviroment with `uv`
```bash
uv sync
```

3. Configure your Chromium path:

Since this project uses a custom system Chromium installation, ensure Chromium is installed on your machine and locate its executable path.

4. Create a Discord Bot (if you haven't already):

If you need help setting up your bot application, check out the [Official Discord Guide](https://docs.discord.com/developers/quick-start/getting-started#step-1-creating-an-app). Make sure to enable `Message Content Intent`

5. Set up your environment variables:

Create a `.env` file in the root directory. Generate a secure `DJANGO_SECRET_KEY` via the terminal:
```bash
uv run python -c 'import django.core.management.utils; print(django.core.management.utils.get_random_secret_key())'
```

Fill out your `.env` file (use `.env.example` for convenience):
```
DJANGO_SECRET_KEY=your-django-secret-key
DJANGO_DEBUG=FALSE
CHROMIUM_EXECUTABLE_PATH=your_executable_path
REGION=EU
DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=your_discord_channel_id
```

6. Run database migrations:

```bash
uv run python manage.py migrate
```

## 🕹️ Usage

Start your Django server using `uv`:
```bash
uv run python manage.py runserver
```

Begin the hourly scraping task:
```bash
uv run python manage.py start_workers
```

Boot up your Discord bot:
```bash
uv run python manage.py discord_bot
```

## 🗺️ Roadmap

- Selecting a region via the Discord bot
- Add pagination to the /item list command

## 📄 Licence