# **qBittaggarr**

A lightweight and customizable qBittorrent tag and torrent rule manager.

**qBittaggarr** is a Docker application that connects to your qBittorrent instance and automatically applies tags and seeding rules to your torrents based on their trackers using defined keywords.

This application is heavily inspired by [qbit_manage](https://github.com/StuffAnThings/qbit_manage), but is designed to be easier to implement, and to handle all things tags in qBittorrent.

# **Features**

* **Tracker Keywords:** Automatically assign any tag you want based on keywords found in a torrent's tracker list.
* **Default Behaviors:** Default tag/torrent behaviors for any torrents that don't meet given criteria.
* **Flexible Seeding Limits:** Define unique seeding rules (ratio and time limits) for each custom tag.
* **"Forever" Override:** Manually add a forever tag to any torrent to give it infinite seeding time and ratio.
* **Speed Limits:** COMING SOON. Apply download/upload speed limits based on tag.
* **Name Keywords:** COMING SOON. Automatically assign any tag you want based on keywords found in a torrent's name.
* **Completed Torrent Handling:** COMING SOON. Apply completed torrent handling behaviors based on tag.
* **Super Seeding:** COMING SOON. Apply super seeding behaviors based on tag.

# **Getting Started**

## Prerequisites

* A running qBittorrent instance with the Web UI enabled.

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
      - ./path/to/your/config.yml
    environment:
      - HOME=/app
      - PYTHONIOENCODING=utf-8
      - LANG=C.UTF-8
    restart: unless-stopped
```
4. Start the application.
