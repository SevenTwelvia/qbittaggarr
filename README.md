# **qBittaggarr**

A simple, lightweight, and customizable qBittorrent tag and seeding rule manager.

**qBittaggarr** is a Docker application that connects to your qBittorrent instance and automatically applies tags and seeding rules to your torrents based on their trackers using defined keywords.

# **Features**


* **Customizable Rules:** Automatically assign any tag you want based on keywords found in a torrent's tracker list.
* **Flexible Seeding Limits:** Define unique seeding rules (ratio and time limits) for each custom tag.
* **"Forever" Override:** Manually add a forever tag to any torrent to give it infinite seeding time and ratio.
* **Quiet Operation:** By default, the script only logs a summary of its actions at the end of each cycle.
* **Verbose Logging:** An optional setting for detailed, per-torrent logging, perfect for debugging or initial setup.
* **Dry Run Mode:** Test your rules and see what the script would do without making any actual changes to qBittorrent.

# **Getting Started**

## Prerequisites

* A running qBittorrent instance with the Web UI enabled.

* Docker installed. Docker Compose is recommended for the simplest setup.

## Installation
1. Create a directory for your qbittaggarr configuration.
2. Create your config.yml file. Copy the contents from [config.yml](https://github.com/SevenTwelvia/qbittaggarr/blob/main/config.yml) and edit it to match your setup.
3. Pull this image:
```
services:
  qbittaggarr:
    image: ghcr.io/seventwelvia/qbittaggarr:latest
    container_name: qbittaggarr
    volumes:
      - ./path/to/you/config.yml
    environment:
      - HOME=/app
      - PYTHONIOENCODING=utf-8
      - LANG=C.UTF-8
    restart: unless-stopped
```
4. Start the application.
