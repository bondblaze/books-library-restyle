import requests
import os
from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename

HOME_URL = "https://tululu.org"


def check_for_redirect(response):
    for resp in response.history:
        if resp.status_code != 200 or response.url == "https://tululu.org/":
            raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    response.raise_for_status()

    filepath = os.path.join(folder, sanitize_filename(filename) + '.txt')
    print(filepath)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def main():
    Path("books").mkdir(parents=True, exist_ok=True)
    for i in range(1, 11):
        url = f"https://tululu.org/b{i}/"
        response = requests.get(url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            book_title = soup.find('h1').text.split('::')
            download_url = soup.find('a', string='скачать txt', href=True)
            if download_url is not None:
                download_txt(HOME_URL + download_url['href'], f"{i}." + book_title[0].strip(), folder='books/')
        except requests.HTTPError:
            continue


if __name__ == '__main__':
    main()
