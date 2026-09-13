# ----- Modules -----
import requests
import random
import os

# ----- Global Variables -----
TAGS = ["yuri"]

images_ids = set()

# ----- Fetch the Posts from Safebooru -----
def search_images(tags=TAGS, limit=1000):
    try:
        base_url = "https://safebooru.org/index.php"
        params = {
            "page": "dapi",
            "s": "post",
            "q": "index",
            "json": 1,
            "tags": "+".join(tags),
            "limit": limit
        }
        response = requests.get(base_url, params=params, timeout=10)
        if response.status_code != 200:
            print(f"ERROR IN 'search_images': Status {response.status_code}")
            return []
        return response.json()
    except (requests.exceptions.RequestException, ValueError):
        print("ERROR WHILE TRYING TO FETCH THE IMAGES")
        return []

# ----- Choose 1 Post randomly -----
def pick_random_post(posts):
    if not posts: return None
    available = [p for p in posts if p.get("id") not in images_ids]
    if not available:
        images_ids.clear()
        available = posts
    post = random.choice(available)
    images_ids.add(post.get("id"))
    return post

# ----- Extract the Image from the Post -----
def extract_image_url(post):
    if not post: return None
    return post.get("sample_url") or post.get("file_url")

# ----- Download the Image for OBS and save it in the "temp_images" Folder -----
def download_image(url, post_id, save_path="images/"):
    try:
        os.makedirs(save_path, exist_ok=True)
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"ERROR IN 'download_image': Status {response.status_code}")
            return None
        file_ending = response.headers.get("content-type").split("/")[-1]
        file_path = f"{save_path}{post_id}.{file_ending}"
        with open(file_path, "wb") as f:
            f.write(response.content)
        return file_path
    except (requests.exceptions.RequestException, ValueError):
        print("ERROR WHILE TRYING TO DOWNLOAD THE IMAGE")
        return None

# ----- The COMPLETE Algorithm to create 1 single Yuri Image -----
def get_random_yuri_image(posts):
    post = pick_random_post(posts)
    url = extract_image_url(post)
    if url:
        path = download_image(url, post.get("id"))
        return path
    return None

# ----- Testing -----
if __name__ == '__main__':
    posts = search_images() # Should run about every 10 Minutes 
    for i in range(10):
        print(f"---------- {i + 1} ----------")
        path = get_random_yuri_image(posts)
        print(path)