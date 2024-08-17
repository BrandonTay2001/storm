from flask_cors import CORS
from flask import Flask, request, render_template
from generate import generateMain
import shutil
import shutil
import json
import os
from knowledge_storm import STORMWikiRunnerArguments, STORMWikiRunner, STORMWikiLMConfigs
from knowledge_storm.lm import OpenAIModel
from knowledge_storm.rm import SerperRM
from convertToHTML import convertToHTML

from dotenv import load_dotenv
load_dotenv()

lm_configs = STORMWikiLMConfigs()
openai_kwargs = {
    'api_key': os.getenv('OPENAI_API_KEY'),
    'temperature': 0.2,
    'top_p': 0.9,
}

gpt_4_mini = OpenAIModel(model='gpt-4o-mini', max_tokens=500, **openai_kwargs)
gpt_4 = OpenAIModel(model='gpt-4o', max_tokens=3000, **openai_kwargs)
lm_configs.set_conv_simulator_lm(gpt_4_mini)
lm_configs.set_question_asker_lm(gpt_4_mini)
lm_configs.set_outline_gen_lm(gpt_4_mini)
lm_configs.set_article_gen_lm(gpt_4)
lm_configs.set_article_polish_lm(gpt_4)
engine_args = STORMWikiRunnerArguments(output_dir='outputs', max_thread_num=5)
data = {"autocorrect": True, "num": 10, "page": 1}
rm = SerperRM(serper_search_api_key=os.getenv('SERPER_API_KEY'), query_params=data)
runner = STORMWikiRunner(engine_args, lm_configs, rm)

app = Flask(__name__)
CORS(app)

@app.route('/generateReportOld', methods=['POST'])
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
            add = f'<p>[{i + 1}]: <a href={url} target="_blank">{url}</a></p>'
            html += add + '\n'
        # delete the entire output directory
        shutil.rmtree(final_output_dir)
        return html
    except Exception as e:
        return str(e)

@app.route('/generateReport', methods=['POST'])
def generate_report2():
    topic = request.json['topic']
    output_dir = 'outputs'
    article_dir_name = topic.replace(' ', '_').replace('/', '_')
    final_output_dir = os.path.join(output_dir, article_dir_name)
    runner.run(topic=topic, do_research=True, do_generate_outline=True, do_generate_article=True, do_polish_article=False)
    runner.post_run()
    runner.summary()
    # convert storm_gen_article.txt to .md file
    shutil.copyfile(f'{final_output_dir}/storm_gen_article.txt', f'{final_output_dir}/storm_gen_article.md')
    html = convertToHTML(f'{final_output_dir}/storm_gen_article.md')
    with open(f'{final_output_dir}/url_to_info.json') as f:
        url_to_info = json.load(f)
    urls_unsorted = url_to_info['url_to_unified_index']
    sorted_items = sorted(urls_unsorted.items(), key=lambda item: item[1])
    sorted_urls = [item[0] for item in sorted_items]
    html += "\n\n<h2>Reference URLs</h2>"
    for i, url in enumerate(sorted_urls):
        add = f'<p>[{i + 1}]: <a href={url} target="_blank">{url}</a></p>'
        html += add + '\n'
    # delete the entire output directory
    shutil.rmtree(final_output_dir)
    return html

@app.route('/')
def test():
    return "Hello World"

if __name__ == '__main__':
    app.run(host="0.0.0.0", threaded=True, port=5001)