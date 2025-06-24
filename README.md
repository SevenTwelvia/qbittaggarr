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
3. Install this image:
```
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
```
4. Start the application.

### **Configuration**
All configuration is done in the config.yml file.


```
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
  # The main key (e.g., "private", "private-tracker-A") will be used as the tag.
  custom_tags:
    # Example Rule 1: For a specific private tracker
    private:
      keywords: ["private-tracker-one.com", "keyword-for-tracker-one"]
      ratio: 10.0 
      seeding_time_limit: 30 # in days

    # Example Rule 2: For a different type of content
    # yourfavoriteprivatetracker:
    #   keywords: ["favorite", "privatetracker"]
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
```
