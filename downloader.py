import urllib.request
import json
import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_PAGE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width">
  <title>TITLE</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-gH2yIJqKdNHPEq0n4Mqa/HGKIhSkIHeL5AyhkYV8i59U5AR6csBvApHHNl/vI1Bx" crossorigin="anonymous">
  <style>
.paragraph {
  margin: 10px 0px;
}
img {
  max-width: 600px;
}
.perseus-sr-only {
  display: none;
}
li.perseus-radio-option {
  list-style-type: none;
}
  </style>
</head>
<body>
<div class="container container-md">
<h1>TITLE</h1>
BODY
</div>
</body>
</html>
"""

def download_unit(url):
  try:
    response = urllib.request.urlopen(url)
  except urllib.error.HTTPError:
    print('ERROR: Chapter could not be opened', url)
  html = response.read()
  soup = BeautifulSoup(html, 'html.parser')
  title = soup.select_one('[data-test-id=unit-block-title]').get_text()

  unit_slug = url.split('/')[-1]
  if unit_slug.find(':') > 0:
    unit_slug = unit_slug.split(':')[1]
  unit_folder = f"en/{unit_slug}"
  toc_html = f"<h1>{unit_slug}</h1>"
  lessons = soup.select('[data-test-id="lesson-card"]')
  for lesson in lessons:
    links = lesson.find_all('a')
    lesson_title = links[0].get_text()
    toc_html += f'<h2>{lesson_title}</h2>'
    toc_html += '<ul>'
    for link in links[1:]:
      if link['href'].find('/a/') < 0:
        continue
      link_text = link.get_text().replace("(Opens a modal)", "")
      link_url = f"https://www.khanacademy.org{link['href']}".split("?")[0]
      article_slug = link_url.split('/')[-1]
      filename = f"{article_slug}.html"
      toc_html += f'<li><a href="{filename}">{link_text}</a></li>'
      download_article(link_url, f"{unit_folder}/{filename}")
    toc_html += '</ul>'
  toc_html = BASE_PAGE.replace('TITLE', title).replace('BODY', toc_html)
  f = open(f"{unit_folder}/index.html", "w")
  f.write(toc_html)
  f.close() 

def download_article(url, filename):
  slug = url.split('/')[-1]
  options = Options()
  options.headless = True
  options.add_argument("--window-size=1920,1200")

  DRIVER_PATH = '/Applications/chromedriver'
  driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)
  driver.get(url)
  title = driver.title
  html = driver.page_source
  driver.quit()
  soup = BeautifulSoup(html, 'html.parser')
  article = soup.select_one('.bibliotron-article')
  iframes = article.find_all('iframe')
  for iframe in iframes:
    if iframe['src'].find('/program/') > -1:
      program_id = iframe['src'].split('/program/')[1].split('/embedded')[0]
      program_url = f'https://www.khanacademy.org/api/internal/show_scratchpad?scratchpad_id={program_id}'
      response = urllib.request.urlopen(program_url)
      program_data = json.loads(response.read())
      code = program_data['scratchpad']['revision']['code']
      pre = soup.new_tag('pre')
      pre.string = code
      iframe.replace_with(pre)
  article_html = str(article).replace("<table>", "<table class='table'>")
  article_html = re.sub(r'<div style="padding-bottom: (\d\d\.?\d?\d?%);"><\/div>', '', article_html)
  page_html = BASE_PAGE.replace('BODY', article_html).replace('TITLE', title)
  f = open(filename, 'w')
  f.write(page_html)
  f.close()

download_unit('https://www.khanacademy.org/computing/ap-computer-science-principles/x2d2f703b37b450a3:digital-information')
download_unit('https://www.khanacademy.org/computing/ap-computer-science-principles/programming-101')
download_unit('https://www.khanacademy.org/computing/ap-computer-science-principles/the-internet')
download_unit('https://www.khanacademy.org/computing/ap-computer-science-principles/algorithms-101')
download_unit('https://www.khanacademy.org/computing/ap-computer-science-principles/data-analysis-101')
download_unit('https://www.khanacademy.org/computing/ap-computer-science-principles/x2d2f703b37b450a3:simulations')
download_unit('https://www.khanacademy.org/computing/ap-computer-science-principles/x2d2f703b37b450a3:online-data-security')
download_unit('https://www.khanacademy.org/computing/ap-computer-science-principles/x2d2f703b37b450a3:computing-innovations')
