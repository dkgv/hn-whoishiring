# hn-whoishiring
 
Lightweight Hacker News scraper for the monthly "Ask HN: Who is hiring?" threads.

## Usage
1. Clone the repository `git clone https://github.com/dkgv/hn-whoishiring.git`
2. Install the necessary packages with `pip install -r requirements.txt` (consider using `virtualenv`)
3. Lookup the relevant Hacker News thread id, i.e. `https://news.ycombinator.com/item?id=<thread_id>`
4. Run the scraper with the thread id passed `python scraper.py <thread_id>`
5. Examine the jobs directly with `ack`, `grep`, or manually by sifting through `dump-latest.json`