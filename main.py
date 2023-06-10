import requests
import os

from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib.parse import urlsplit

HOME_URL = 'https://tululu.org'


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


def parse_book_page(response: requests):
    soup = BeautifulSoup(response.text, 'lxml')

    book_title = soup.find('h1').text.split('::')
    genres = [genre.get_text() for genre in soup.find('span', class_='d_book').find_all('a')]
    comments = soup.find('div', id='content').find_all('div', class_='texts')
    comments_sanitized = [comment.find('span').text for comment in comments]

    download_url = soup.find('a', string='скачать txt')

    txt_url = ''
    if download_url is not None:
        txt_url = urljoin(HOME_URL, download_url['href'])

    image_url = urljoin(HOME_URL, soup.find('div', class_='bookimage').find('img')['src'])

    return {
        'Название': book_title[0].strip(),
        'Автор': book_title[1].strip(),
        'Жанр': genres,
        'Комментарии': comments_sanitized,
        'Ссылка для скачивания': txt_url,
        'Ccылка на картинку': image_url
    }


def main():
    Path("books").mkdir(parents=True, exist_ok=True)
    Path("images").mkdir(parents=True, exist_ok=True)

    for count in range(1, 11):
        url = f"{HOME_URL}/b{count}/"
        response = requests.get(url)
        response.raise_for_status()

        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        book_page = parse_book_page(response)

        print(f"Название: {book_page['Название']}")
        print(f"Автор: {book_page['Автор']}")

        if book_page['Ссылка для скачивания'] != '':
            download_txt(book_page['Ссылка для скачивания'], f"{count}." + book_page['Название'], folder='books/')

        download_image(book_page['Ccылка на картинку'], folder='images/')


if __name__ == '__main__':
    main()
