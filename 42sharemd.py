import pandas as pd
import os
import re
import requests
from bs4 import BeautifulSoup

def clean_filename(filename):
    invalid_chars = r'[\\/*?:"<>|]'
    cleaned_filename = re.sub(invalid_chars, "", filename)
    cleaned_filename = re.sub(r'\n', "", cleaned_filename)  # 清理换行符
    return cleaned_filename

def write_to_md_file(content, filename, directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    new_filename = filename
    file_counter = 1
    while os.path.exists(os.path.join(directory, new_filename)):
        base_name, extension = os.path.splitext(filename)
        new_filename = f"{base_name}-{file_counter}{extension}"
        file_counter += 1

    with open(os.path.join(directory, new_filename), 'w', encoding='utf-8') as f:
        f.write(content)


def format_to_md(questions, answers):
    md = ""
    for q, a in zip(questions, answers):
        #   前后有回车多一行
        #   md += f"**来自你的消息：**\n\n{q}\n\n**来自 ChatGPT 的消息：**\n\n{a}\n\n"
        #   前后没有空行
        md += f"**来自你的消息：**\n{q}\n\n**来自 ChatGPT 的消息：**\n{a}\n\n"
    return md

def get_content_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # get title
    title_element = soup.find("title")
    if title_element:
        title = title_element.text
        # remove ' - 42Share' from the title
        title = title.replace('... - 42Share', '')
    else:
        title = "No Title"

    # find all chat messages
    messages = soup.select('[class^="pb-2 whitespace-prewrap"], [class^="utils_response"]')
    questions = []
    answers = []
    for i, message in enumerate(messages):
        if message:
            if i % 2 == 0:
                questions.append(message.text)
            else:
                answers.append(message.text)

    return title, questions, answers




def process_links_from_file(file_path):
    df = pd.read_csv(file_path, header=None)  # 设置 header=None，表示没有表头
    links = df.iloc[:, 0]
    print(f"Total links: {len(links)}")
    for link in links:
        print(f"Processing link: {link}")
        if link.startswith('http'):
            try:
                title, questions, answers = get_content_from_url(link)
                md_content = format_to_md(questions, answers)
                filename = clean_filename(f"{title}.md")
                write_to_md_file(md_content, filename, 'output')
            except Exception as e:
                print(f"Error processing link {link}: {e}")

process_links_from_file('link.csv')

