import time
import yaml
import os
import traceback
import sys
from urllib.parse import urlparse

from qbittorrentapi import Client, LoginFailed

def load_config():
    """Loads configuration from config.yml."""
    try:
        # Use sys.stdout.flush() to ensure prints appear immediately in container logs
        print("Loading configuration from config.yml...", flush=True)
        with open('config.yml', 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print("Error: config.yml not found. Please create a config.yml file.", flush=True)
        exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Could not parse config.yml. Please check its format. Details: {e}", flush=True)
        exit(1)

def main():
    """Main function to run the torrent management logic."""
    config = load_config()

    # --- Configuration for run mode ---
    dry_run = config.get('dry_run', True) # Default to dry_run=True for safety
        
    # --- Configuration for verbose logging ---
    verbose_logging = config.get('verbose_logging', False)

    # --- Banners for Dry and Live modes ---
    box_width = 58
    print("\n╔" + "═" * box_width + "╗")
    if dry_run:
        print("║" + "DRY RUN MODE ENABLED".center(box_width) + "║")
        print("║" + "No actual changes will be made to qBittorrent.".center(box_width) + "║")
    else:
        print("║" + "LIVE MODE ENABLED".center(box_width) + "║")
        print("║" + "This script WILL make changes to qBittorrent.".center(box_width) + "║")
    print("╚" + "═" * box_width + "╝", flush=True)

    # qBittorrent client configuration
    host = config.get('qbittorrent', {}).get('host')
    port = config.get('qbittorrent', {}).get('port')
    username = config.get('qbittorrent', {}).get('username')
    password = config.get('qbittorrent', {}).get('password')

    # --- Rule configuration ---
    custom_tags_rules = config.get('rules', {}).get('custom_tags', {})
    default_tags_rules = config.get('rules', {}).get('default_tags', {})
    all_rules = {**custom_tags_rules, **default_tags_rules}

    # Connect to qBittorrent with a timeout
    qbt_client = Client(
        host=f"{host}:{port}",
        username=username,
        password=password,
        REQUESTS_ARGS={'timeout': 30}
    )

    try:
        qbt_client.auth_log_in()
        print("Successfully connected to qBittorrent.", flush=True)
    except Exception as e:
        print(f"\n!!!!!!!!!!!!!!!!!!!!!!!!! CONNECTION FAILED !!!!!!!!!!!!!!!!!!!!!!!!!")
        print(f"Could not connect to qBittorrent at {host}:{port}.")
        print("Please check your host, port, username, and password in config.yml.")
        print(f"Error details: {e}")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!", flush=True)
        return

    while True:
        start_time = time.time()
        
        # --- Initialize counters for the summary ---
        tags_applied = {tag: 0 for tag in all_rules.keys()}
        rules_applied = {tag: 0 for tag in all_rules.keys()}
        torrents_checked = 0
        total_torrents = 0

        try:
            torrent_hashes = [t.hash for t in qbt_client.torrents_info()]
            total_torrents = len(torrent_hashes)
            
            print(f"\n---> Starting new cycle. Found {total_torrents} torrents to check.", flush=True)

            for i, torrent_hash in enumerate(torrent_hashes):
                torrents_checked += 1
                try:
                    torrent = qbt_client.torrents_info(torrent_hashes=torrent_hash)[0]
                    current_tags = torrent.tags.split(',') if torrent.tags else []
                    
                    # --- Rule Logic ---
                    prospective_tag = None
                    
                    if 'forever' in current_tags:
                        prospective_tag = 'forever'
                    else:
                        all_trackers = qbt_client.torrents_trackers(torrent_hash=torrent.hash)
                        working_trackers = [t for t in all_trackers if t.status in (2, 3)]
                        tracker_urls = [t.url for t in working_trackers]
                        
                        for tag_name, tag_data in custom_tags_rules.items():
                            if any(keyword in url for url in tracker_urls for keyword in tag_data.get('keywords', [])):
                                prospective_tag = tag_name
                                break
                        
                        if not prospective_tag:
                            prospective_tag = 'public'

                    target_rule = all_rules.get(prospective_tag, {})
                    target_ratio_limit = float(target_rule.get('ratio', -1))
                    target_seeding_time_days = int(target_rule.get('seeding_time_limit', -1))
                    target_seeding_time_minutes = -1 if target_seeding_time_days == -1 else target_seeding_time_days * 24 * 60

                    tag_action_needed = prospective_tag not in current_tags and prospective_tag != 'forever'
                    rules_action_needed = (torrent.ratio_limit != target_ratio_limit or torrent.seeding_time_limit != target_seeding_time_minutes)

                    if tag_action_needed or rules_action_needed or verbose_logging:
                        print(f"\nProcessing torrent {i+1}/{total_torrents}: {torrent.name} (Hash: {torrent.hash[-6:]})", flush=True)

                        if verbose_logging and prospective_tag != 'forever':
                            if not tracker_urls:
                                print("  - No working trackers found for this torrent.")
                            else:
                                print("  - Working trackers found:")
                                for url in tracker_urls:
                                    print(f"    - {url}")
                            sys.stdout.flush()

                        # Perform actions
                        if tag_action_needed:
                            print(f"  - Determined Tag: '{prospective_tag}' (will be applied).", flush=True)
                            tags_applied[prospective_tag] += 1
                            if not dry_run:
                                qbt_client.torrents_add_tags(tags=prospective_tag, torrent_hashes=[torrent.hash])
                        
                        if rules_action_needed:
                            seeding_time_log = "infinite" if target_seeding_time_days == -1 else f"{target_seeding_time_days} days"
                            ratio_log = "infinite" if target_ratio_limit == -1.0 else target_ratio_limit
                            print(f"  - Applying rules for tag '{prospective_tag}': Ratio={ratio_log}, Time={seeding_time_log}", flush=True)
                            rules_applied[prospective_tag] += 1
                            if not dry_run:
                                qbt_client.torrents_set_share_limits(
                                    ratio_limit=target_ratio_limit,
                                    seeding_time_limit=target_seeding_time_minutes,
                                    inactive_seeding_time_limit=-1,
                                    torrent_hashes=[torrent.hash]
                                )
                        
                        if not tag_action_needed and not rules_action_needed and verbose_logging:
                            print("  - All tags and rules are already correct.", flush=True)
                
                except Exception as e:
                    print(f"\n---!!! An error occurred processing torrent with hash {torrent_hash} !!!---", flush=True)
                    traceback.print_exc()

        except Exception as e:
            print("\n!!!!!!!!!!!!!!!!!!!!!!! CRITICAL ERROR !!!!!!!!!!!!!!!!!!!!!!!", flush=True)
            traceback.print_exc()

        # --- Summary Print ---
        end_time = time.time()
        duration = round(end_time - start_time, 2)
        
        def print_left_aligned(text):
            print(f"║ {text.ljust(box_width - 2)} ║")
            
        def print_separator(title=""):
            if title:
                padded_title = f" {title} "
                print(f"╠{padded_title.center(box_width, '─')}╣")
            else:
                print(f"╠{'═' * box_width}╣")

        print("\n╔" + "═" * box_width + "╗")
        print(f"║{'CYCLE SUMMARY'.center(box_width)}║")
        print_separator()
        print_left_aligned(f"Torrents Checked: {torrents_checked}/{total_torrents}")
        print_left_aligned(f"Cycle Duration: {duration} seconds")
        
        print_separator("Tag Changes Applied")
        if not any(tags_applied.values()):
             print_left_aligned("  - None")
        else:
            for tag, count in tags_applied.items():
                 if count > 0:
                    print_left_aligned(f"  - {tag.capitalize()}: {count}")

        print_separator("Seeding Changes Applied")
        if not any(rules_applied.values()):
            print_left_aligned("  - None")
        else:
            for tag, count in rules_applied.items():
                if count > 0:
                    print_left_aligned(f"  - {tag.capitalize()}: {count}")
        print("╚" + "═" * box_width + "╝", flush=True)

        update_interval = config.get('update_interval_seconds', 300)
        print(f"\n---> Cycle complete. Waiting for {update_interval} seconds...", flush=True)
        time.sleep(update_interval)

if __name__ == "__main__":
    main()
