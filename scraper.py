import sys
import json
import requests
from typing import List
from collections import namedtuple
from bs4 import BeautifulSoup

hackernews = 'https://news.ycombinator.com/'
Job = namedtuple('Job', ['header', 'description'])
Comment = namedtuple('Comment', ['user', 'url', 'content'])


def extract_comments(page: BeautifulSoup) -> List[Comment]:
    comments = []
    rows = page.find_all('tr', {'class': ['athing', 'comtr']})
    for row in rows:
        # Find owner of comment
        user_elem = row.find('a', {'class': 'hnuser'})
        if not user_elem:
            continue
        user = user_elem.text

        # Find comment permalink
        url = row.find('span', {'class': 'age'}).find('a').attrs.get('href')
        url = hackernews + url

        # Find comment content
        content_elem = row.find('span', {'class': ['commtext', 'c00']})
        if not content_elem or '|' not in content_elem.text:
            continue

        content = content_elem.text
        header = content

        # Expand links and trim header
        for p in content_elem.find_all('p'):
            header = header.replace(p.text, '')
            a = p.find('a')
            if a and '...' in a.text:
                content = content.replace(a.text, a.attrs.get('href'))

        # Refit content
        content = content.replace(header, '')
        content = header + '\n' + content

        # Save comment
        comments.append(Comment(user, url, content))
    return comments


def comment_to_job(comment: Comment) -> Job:
    lines = comment.content.split('\n')
    if len(lines) <= 1:
        return None
    header = lines[0]
    if '|' not in header:
        return None
    description = comment.content.replace(header, '').strip()
    return Job(header, description)


def extract_jobs(page: BeautifulSoup) -> List[Job]:
    return [comment_to_job(comment) for comment in extract_comments(page)]


def scrape_jobs_recursively(url: str, all_jobs: List[Job] = None):
    r = requests.get(url)
    if r.status_code != 200:
        return

    # Extract jobs for current page
    soup = BeautifulSoup(r.text, 'html.parser')
    jobs = extract_jobs(soup)
    if not jobs:
        return

    # Filter away unparseable jobs
    all_jobs.extend([job for job in jobs if job])

    # Attempt to find URL for next page
    next_url_elem = soup.find('a', {'class': 'morelink'})
    if not next_url_elem:
        return

    # Scrape next page
    next_url = hackernews + next_url_elem.attrs.get('href')
    scrape_jobs_recursively(next_url, all_jobs)


if __name__ == '__main__':
    thread_id = sys.argv[1]
    base_url = hackernews + 'item?id={}'.format(thread_id)
    jobs = []
    scrape_jobs_recursively(base_url, jobs)
    with open('dump-latest.json', 'w') as f:
        json.dump([job._asdict() for job in jobs], f)
    for job in jobs:
        print(job.header)
        print(job.description)
        print()
