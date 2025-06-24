# <b>qbittaggarr</b>

A simple, lightweight, and customizable qBittorrent tag and seeding rule manager.

<b>qbittaggarr</b> is a Docker application that connects to your qBittorrent instance and automatically applies tags and seeding rules to your torrents based on their trackers using defined keywords.

# <b>Features</b>


<li><b>Customizable Rules:</b> Automatically assign any tag you want based on keywords found in a torrent's tracker list.</li>
<li><b>Flexible Seeding Limits:</b> Define unique seeding rules (ratio and time limits) for each custom tag.</li>
<li><b>"Forever" Override:</b> Manually add a forever tag to any torrent to give it infinite seeding time and ratio.</li>
<li><b>Quiet Operation:</b> By default, the script only logs a summary of its actions at the end of each cycle.</li>
<li><b>Verbose Logging:</b> An optional setting for detailed, per-torrent logging, perfect for debugging or initial setup.</li>
<li><b>Dry Run Mode:</b> Test your rules and see what the script would do without making any actual changes to qBittorrent.</li>

Getting Started
Prerequisites
A running qBittorrent instance with the Web UI enabled.

Docker installed. Docker Compose is recommended for the simplest setup.

Installation
Create a directory for your qbittaggarr configuration.

mkdir /path/to/your/appdata/qbittaggarr
cd /path/to/your/appdata/qbittaggarr

Inside that new directory, create a config.yml file. Copy the contents from the example in the Configuration section below and edit it to match your setup.

To run the application, create a docker-compose.yml file in the same directory. You have two options:

Option A: Use a Pre-built Image (Recommended)
This is the easiest method. It pulls the ready-to-use image from a Docker registry.

# docker-compose.yml
version: '3.8'
services:
  qbittaggarr:
    image: ghcr.io/your-github-username/qbittaggarr:latest # Replace with your actual image path
    container_name: qbittaggarr
    volumes:
      - ./config.yml:/app/config.yml:ro
    environment:
      - HOME=/app
      - PYTHONIOENCODING=utf-8
      - LANG=C.UTF-8
    # For systems like TrueNAS/Unraid, you might need to set the PUID/PGID
    # user: "568:568"
    restart: unless-stopped

Note: You would replace ghcr.io/your-github-username/qbittaggarr:latest with the actual path once the image is published to a registry like GitHub Container Registry or Docker Hub.

Option B: Build from Source
Use this method if you want to modify the code. You will need to have the Dockerfile, main.py, and requirements.txt from this repository in the same directory as your docker-compose.yml.

# docker-compose.yml
version: '3.8'
services:
  qbittaggarr:
    build:
      context: .
    container_name: qbittaggarr
    volumes:
      - ./config.yml:/app/config.yml:ro
    environment:
      - HOME=/app
      - PYTHONIOENCODING=utf-8
      - LANG=C.UTF-8
    # For systems like TrueNAS/Unraid, you might need to set the PUID/PGID
    # user: "568:568"
    restart: unless-stopped

Start the application:

docker-compose up -d

To see the logs, run docker-compose logs -f.

Configuration
All configuration is done in the config.yml file.

# config.yml

# Your qBittorrent Web UI connection details
qbittorrent:
  host: "your-qbit-host"  # e.g., 192.168.1.10 or qbittorrent.local
  port: 8080
  username: "your-qbit-username"
  password: "your-qbit-password"

# Set to true to log actions without making changes.
# Highly recommended for the first run!
dry_run: true

# Set to true for detailed, per-torrent logging.
# Set to false for quiet operation (only logs actions and summaries).
verbose_logging: false

rules:
  # Define your custom tags and their rules here.
  # The script will check them in order and apply the first match it finds.
  # The main key (e.g., "movies-hd", "private-tracker-A") will be used as the tag.
  custom_tags:
    # Example Rule 1: For a specific private tracker
    private:
      keywords: ["private-tracker-one.com", "keyword-for-tracker-two"]
      ratio: 10.0
      seeding_time_limit: 30 # in days

    # Example Rule 2: For a different type of content
    # linux-isos:
    #   keywords: ["ubuntu", "debian", "archlinux"]
    #   ratio: 2.0
    #   seeding_time_limit: 7 # in days

  # Define the fallback and override tags.
  default_tags:
    # This tag is applied if a torrent matches NO custom rules.
    public:
      ratio: 1.0
      seeding_time_limit: 1 # in days
      
    # This tag is a manual override.
    forever:
      ratio: -1
      seeding_time_limit: -1

# How often the script should check your torrents, in seconds.
update_interval_seconds: 300
