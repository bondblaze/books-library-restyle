import requests
import os

from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib.parse import urlsplit

HOME_URL = "https://tululu.org"


def check_for_redirect(response):
    for resp in response.history:
        if resp.status_code != 200 or response.url == HOME_URL:
            raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    response.raise_for_status()

    filepath = os.path.join(folder, sanitize_filename(filename) + '.txt')

    with open(filepath, 'wb') as file:
        file.write(response.content)


def download_image(url, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()

    img_name = str(urlsplit(url).path.split('/')[2])

    filepath = os.path.join(folder, img_name)

    with open(filepath, 'wb') as file:
        file.write(response.content)


def main():
    Path("books").mkdir(parents=True, exist_ok=True)
    Path("images").mkdir(parents=True, exist_ok=True)

    for i in range(1, 11):
        url = f"{HOME_URL}/b{i}/"
        response = requests.get(url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            book_title = soup.find('h1').text.split('::')
            # print(f"Заголовок: {book_title[0].strip()}")
            download_url = soup.find('a', string='скачать txt', href=True)

            img_url = urljoin(HOME_URL, soup.find('div', class_='bookimage').find('img')['src'])

            if download_url is not None:
                txt_url = urljoin(HOME_URL, download_url['href'])
                download_txt(txt_url, f"{i}." + book_title[0].strip(), folder='books/')

            download_image(img_url, folder='images/')

        except requests.HTTPError:
            continue


if __name__ == '__main__':
    main()
