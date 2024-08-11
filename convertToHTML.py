import markdown

def convertToHTML(file_path):
    with open(file_path, 'r') as file:
        md_content = file.read()

    html = markdown.markdown(md_content)
    return html