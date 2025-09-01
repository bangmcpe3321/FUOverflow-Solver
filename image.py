import requests
import os
import time
import re

def download_file_with_retry(image_url, filepath, cookies, headers, max_retries, retry_delay):
    """
    Downloads a file to a specific filepath with a retry mechanism.
    """
    filename = os.path.basename(filepath)
    for attempt in range(max_retries):
        try:
            response = requests.get(image_url, cookies=cookies, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"[SUCCESS] Downloaded {filename}")
            return True
        except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
            print(f"[ATTEMPT {attempt + 1}/{max_retries}] Failed for {filename}. Error: {e}")
            if attempt + 1 < max_retries:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"[FAILURE] All {max_retries} attempts failed for {filename}.")
    return False

# --- SIMPLIFIED PARSING FUNCTION ---
def parse_url_pattern(url):
    """
    Uses a simple regex to extract the full base name and the attachment ID.
    Example: .../ite302c_-_sp_2025_-_re_3811-webp.199272/
    - Group 1 (base_name): ite302c_-_sp_2025_-_re_3811-webp
    - Group 2 (start_id):  199272
    """
    # This pattern captures the non-slash characters before the final dot and number.
    pattern = re.compile(r"/([^/]+)\.(\d+)/?$")
    
    match = pattern.search(url)
    if match:
        base_name = match.group(1)
        start_id = int(match.group(2))
        return base_name, start_id
    return None, None
# --- END SIMPLIFIED FUNCTION ---

# --- CONFIGURATION ---
MAX_RETRIES = 4
RETRY_DELAY = 5
DOWNLOAD_DIRECTORY = "downloaded_images"
BASE_ATTACHMENT_URL = "https://fuoverflow.com/attachments/"

# --- SCRIPT EXECUTION ---

print("--- XenForo Batch WEBP Downloader ---")
start_url = input("\nEnter the URL of the FIRST image in the sequence: ")
try:
    total_files_str = input("Enter the TOTAL number of images to download: ")
    TOTAL_FILES_TO_DOWNLOAD = int(total_files_str)
except ValueError:
    print("Error: Please enter a valid number.")
    exit()

print("\nEnter your authentication cookies (input will be visible):")
xf_user_value = input("Paste your xf_user cookie value: ")
xf_session_value = input("Paste your xf_session cookie value: ")

# 2. Parse the URL to get the pattern
BASE_NAME, START_ATTACH_ID = parse_url_pattern(start_url)
if BASE_NAME is None:
    print("\nError: Could not parse the URL.")
    print("Please ensure the URL has a pattern like '.../some-filename.123456/'")
    exit()

print(f"\nSuccessfully parsed URL pattern:")
print(f"  - Base Filename: {BASE_NAME}")
print(f"  - Starting ID:   {START_ATTACH_ID}")

# 3. Prepare for Download
auth_cookies = {'xf_user': xf_user_value, 'xf_session': xf_session_value}
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

if not os.path.exists(DOWNLOAD_DIRECTORY):
    os.makedirs(DOWNLOAD_DIRECTORY)

print("\n--- Starting Batch Download ---")

successful_downloads, skipped_files = 0, 0
failed_urls = []

# 4. Execute the Main Download Loop
for i in range(TOTAL_FILES_TO_DOWNLOAD):
    current_attach_id = START_ATTACH_ID + i
    
    # URL is constructed using the full base name parsed from the start URL
    file_url = f"{BASE_ATTACHMENT_URL}{BASE_NAME}.{current_attach_id}/"
    
    # --- CORRECTED FILENAME LOGIC ---
    # Filename is constructed using the base name, the ID, and the known .webp extension
    filename = f"{BASE_NAME}.{current_attach_id}.webp"
    filepath = os.path.join(DOWNLOAD_DIRECTORY, filename)
    
    if os.path.exists(filepath):
        print(f"[SKIPPED] {filename} already exists.")
        skipped_files += 1
        continue

    if download_file_with_retry(file_url, filepath, auth_cookies, headers, MAX_RETRIES, RETRY_DELAY):
        successful_downloads += 1
    else:
        failed_urls.append(file_url)
    
    time.sleep(0.5)

# 5. Final Report
print("\n--- Batch Download Finished ---")
print(f"Summary: {successful_downloads} downloaded, {skipped_files} skipped, {len(failed_urls)} failed (out of {TOTAL_FILES_TO_DOWNLOAD} total).")

if failed_urls:
    print("\nThe following URLs could not be downloaded:")
    for url in failed_urls:
        print(url)