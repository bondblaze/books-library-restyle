import requests
import os
import argparse
import logging
import time

from pathlib import Path
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib.parse import urlsplit

HOME_URL = 'https://tululu.org'

logger = logging.getLogger(__file__)


class BookDownloadPageNotFoundError(TypeError):
    pass


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError(f'Page was redirected to {response.url}')


def download_txt(url, filename, folder='books/'):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

    filepath = os.path.join(folder, sanitize_filename(filename) + '.txt')

    with open(filepath, 'wb') as file:
        file.write(response.content)


def download_image(url, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)

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

    book_download_url = soup.find('a', string='скачать txt')

    if book_download_url:
        txt_url = urljoin(response.url, book_download_url['href'])
    else:
        raise BookDownloadPageNotFoundError(f'Download url not found for page {response.url}')

    image_url = urljoin(response.url, soup.find('div', class_='bookimage').find('img')['src'])

    return {
        'title': book_title[0].strip(),
        'author': book_title[1].strip(),
        'genre': genres,
        'comments': comments_sanitized,
        'txt_url': txt_url,
        'image_url': image_url
    }


def main():
    parser = argparse.ArgumentParser(description='Программа скачивает книги с tululu.org')
    parser.add_argument('--start_id', help='ID книги с которой начать скачивание', type=int, default=1)
    parser.add_argument('--end_id', help='ID книги по которую скачать', type=int, default=10)

    args = parser.parse_args()

    Path('books').mkdir(parents=True, exist_ok=True)
    Path('images').mkdir(parents=True, exist_ok=True)

    for count in range(args.start_id, args.end_id + 1):
        connection = False
        url = f'{HOME_URL}/b{count}/'

        while not connection:
            try:
                response = requests.get(url)
                response.raise_for_status()

                check_for_redirect(response)
                book_title, book_author, book_genre, \
                    book_comments, book_txt_url, book_image_url = parse_book_page(response).values()

                download_txt(book_txt_url, f'{count}.' + book_title, folder='books/')
                download_image(book_image_url, folder='images/')
                logger.info(f'Загружена книга: {book_title}. Автор: {book_author}.')
                connection = True
            except requests.HTTPError as exception:
                logger.error(f'HTTP Error from page {HOME_URL}/b{count}: {exception}')
                connection = True
                continue
            except requests.ConnectionError as exception:
                logger.error(f'Network Connection Error: {exception}')
                time.sleep(30)
                continue
            except BookDownloadPageNotFoundError as exception:
                logger.error(exception)
                connection = True
                continue


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    logger.setLevel(logging.INFO)
    main()
