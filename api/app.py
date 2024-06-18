from flask_cors import CORS
from flask import Flask, request, render_template
from generate import generateMain
import shutil
import json
from convertToHTML import convertToHTML

app = Flask(__name__)
CORS(app)

@app.route('/generateReport', methods=['POST'])
def generate_report():
    try:
        topic = request.json['topic']
        output_dir = 'outputs'
        final_output_dir = generateMain(output_dir, topic)
        # convert the storm_gen_article.md file in the final_output_dir to HTML
        html = convertToHTML(f'{final_output_dir}/storm_gen_article.md')
        with open(f'{final_output_dir}/url_to_info.json') as f:
            url_to_info = json.load(f)
        urls_unsorted = url_to_info['url_to_unified_index']
        sorted_items = sorted(urls_unsorted.items(), key=lambda item: item[1])
        sorted_urls = [item[0] for item in sorted_items]
        html += "\n\n<h2>Reference URLs</h2>"
        for i, url in enumerate(sorted_urls):
            add = f'<p>[{i + 1}]: {url}</p>'
            html += add + '\n'
        # delete the entire output directory
        shutil.rmtree(final_output_dir)
        return html
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    app.run(debug=True, threaded=True)