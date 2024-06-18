from flask_cors import CORS
from flask import Flask, request, render_template_string
import shutil
from convertToHTML import convertToHTML
import json

html = convertToHTML(f'storm_gen_article.md')
# read json file
with open('url_to_info.json') as f:
    url_to_info = json.load(f)
urls_unsorted = url_to_info['url_to_unified_index']
sorted_items = sorted(urls_unsorted.items(), key=lambda item: item[1])
sorted_urls = [item[0] for item in sorted_items]
html += "\n\n<h2>Reference URLs</h2>"
for i, url in enumerate(sorted_urls):
    add = f'<p>[{i + 1}]: {url}</p>'
    html += add + '\n'
# return the html in a file
with open('output.html', 'w') as f:
    f.write(html)