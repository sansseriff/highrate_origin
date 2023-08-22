"""Download files from a figshare collection

See https://docs.figshare.com/ for API documentation.

This script makes three API calls: search for a collection, to get the ID;
request metadata about all articles in the collection; request metadata about
all files in each article.

Then it uses the "download_url" and "name" of each file to download and save to
the working directory.
"""
import argparse
import json
import os
import sys
from tqdm import tqdm
import yaml
import requests
import zipfile


def figshare_get(args=None):
    parser = argparse.ArgumentParser(prog="figshare_get")
    parser.add_argument(
        "search",
        type=str,
        help="Search using a DOI or description of a figshare collection to download",
    )
    parser.add_argument(
        "-n",
        "--result-number",
        required=False,
        type=int,
        help="Download result number (0-9) without prompting",
    )
    args = parser.parse_args(args)

    results = search(args.search)
    if "message" in results:
        print(results)
        sys.exit()
    elif len(results):
        if args.result_number is not None:
            result = results[args.result_number]
        else:
            for i, result in enumerate(results):
                print("  ", i, result["title"], result["doi"])
            result_num_str = input(
                "Type the number of a result to download, or ENTER to skip\n"
            )
            if not len(result_num_str):
                sys.exit()
            else:
                try:
                    result_num = int(result_num_str)
                    result = results[result_num]
                except:
                    print("Did not provide a number in range")
                    sys.exit()

    else:
        print("No results")
        sys.exit()

    collection_id = result["id"]
    download_collection_meta(collection_id)
    download_collection_files(collection_id)


def download_collection_meta(collection_id):
    meta = get_collection(collection_id)
    fname = f"metadata_{collection_id}.json"
    print("Saving metadata to", fname)
    with open(fname, "w") as fd:
        json.dump(meta, fd, indent=2)


def download_collection_files(collection_id):
    for file_meta in get_collection_files(collection_id):
        fname = file_meta["name"]
        if os.path.exists(fname):
            print("Skipping", fname)
        else:
            print("Downloading", fname)
            save_file(file_meta)


def get_collection_files(collection_id):
    article_ids = get_collection_articles(collection_id)
    for article_id in article_ids:
        file_metadata = get_article_files(article_id)
        for file_meta in file_metadata:
            yield file_meta


def search(string):
    url = "https://api.figshare.com/v2/collections/search"
    data = {"search_for": string}
    r = requests.post(url, data=json.dumps(data))
    return r.json()


def get_collection(collection_id):
    url = f"https://api.figshare.com/v2/collections/{collection_id}"
    r = requests.get(url)
    data = r.json()
    return data


def get_collection_articles(collection_id):
    url = f"https://api.figshare.com/v2/collections/{collection_id}/articles?page_size=1000"
    r = requests.get(url)
    data = r.json()
    return [article["id"] for article in data]


def get_article_files(article_id):
    url = f"https://api.figshare.com/v2/articles/{article_id}/files"
    r = requests.get(url)
    data = r.json()
    return data


def save_file(file_meta, path=""):
    r = requests.get(file_meta["download_url"], stream=True)

    with open(os.path.join(path, file_meta["name"]), "wb") as fd:
        for chunk in r.iter_content(chunk_size=1024):
            fd.write(chunk)

def save_file_p(file_meta, path=""):
    r = requests.get(file_meta["download_url"], stream=True)

    with open(os.path.join(path, file_meta["name"]), "wb") as fd:
        total_size = int(file_meta["size"])
        with tqdm(total=total_size, unit="B", unit_scale=True) as pbar:
            for chunk in r.iter_content(chunk_size=1024):
                fd.write(chunk)
                pbar.update(len(chunk))

    # Extract the zip file
    print("Extracting zip file...")
    with zipfile.ZipFile(os.path.join(path, file_meta["name"]), "r") as zip_ref:
        zip_ref.extractall(path)

    if input("Extraction complete. Delete zip file? (y/n)") == "y":
        # Delete the zip file
        os.remove(os.path.join(path, file_meta["name"]))
    


def download_manager():
    print("""Each folder in this repo starts from a number 1-10.
type the number of the folder you want to populate with data:""")
    number = int(input())

    if number< 0 or number > 10:
        print("Number not in range 1-10")
        sys.exit()


    with open("figshare_metadata.yaml", "r") as f:
        metadata = yaml.safe_load(f)

    url = metadata[number]["url"]
    code = url.split("/")[-1]
    path = os.path.join(metadata[number]["path"],"data")

    print(f"Downloading data from figshare code {code} to {path}")
    print("This may take a while...")
    save_file_p(get_article_files(code)[0], path=path)

    print(f"Done! You should now be able to run the code in {metadata[number]['path'] + '/src'}")

    

if __name__ == "__main__":
    download_manager()