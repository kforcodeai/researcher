import arxiv
import argparse
import PyPDF2
import os
import json
import nltk
from rake_nltk import Rake

import fitz
from PIL import Image, ImageDraw
import re
import shutil
import datetime
from tqdm import tqdm

nltk.download("stopwords")
nltk.download("punkt")


def refine_query(query):
    rake = Rake()
    rake.extract_keywords_from_text(query)
    keywords = rake.get_ranked_phrases()
    return " ".join(keywords)


def extract_features_from_pdf(pdfilepath):
    os.makedirs(f"{pdfilepath[:-4]}/imgs/", exist_ok=True)
    doc = fitz.open(pdfilepath)
    zoom = 2
    mat = fitz.Matrix(zoom, zoom)
    count = 0
    # Count variable is to get the number of pages in the pdf
    for p in doc:
        count += 1
    
    matches = []
    cites = []
    external_links = []
    for i in tqdm(range(count)):
        val = f"image_{i+1}.png"
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=mat)
        text = page.get_text()
        link = page.first_link
        while link: # iterate over the links on page
            # do something with the link, then:
            if 'cite' in str(link.uri):
                cites.append(link.uri)
            elif link.is_external:
                external_links.append(link.uri)
            link = link.next

        # does this page has refrence
        match = re.findall(pattern='arXiv:[0-9.]+', string=text)
        fig = page.get_drawings()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        draw = ImageDraw.Draw(img)
        for fg in fig:
            rect = fg['rect']
            # print(rect)
            rect = [rect[0]*img.width, rect[1]*img.height, rect[2]*img.width, rect[3]*img.height]
            rect = [x/1000 for x in rect]
            # print(rect)
            draw.rectangle(rect, outline='red', width=2)    
        img.save(f"{pdfilepath[:-4]}/imgs/{val}")
        matches+=match
    doc.close()
    return matches, list(set(cites)), list(set(external_links))

def extract_features_from_arxiv(p):
    title = p.title
    summary = p.summary

    if p.comment:
        conference = "".join(p.comment.split()[-2])
    else:
        conference = None
    return (title, conference, summary)

def scrape_papers(query, numresults=5):
    refined_query = refine_query(query)
    nw = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')[:-3]
    os.makedirs(f"../artifacts/{nw}", exist_ok=True)
    results = []

    search = arxiv.Search(
        query=refined_query,
        max_results=numresults,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    papers = list(search.results())

    results = []

    for i, p in tqdm(enumerate(papers)):
        text = ""
        file_path = f"../artifacts/{nw}/{str(p).split('/')[-1]}.pdf"
        p.download_pdf(filename=file_path)
        title, conference, summary = extract_features_from_arxiv(p)
        related_paper_ids, cites, links = extract_features_from_pdf(file_path)
        res = {}
        res['title'] = title
        res['conference'] = conference
        res['summary'] = summary
        # res['keywords'] = list(set(refine_query(summary).split()))
        res['related_papers'] = related_paper_ids
        res['cites'] = cites
        res['links'] = links
        results.append(res)
    
    with open(f'../artifacts/{nw}/result.json', 'w') as f:
        json.dump(fp=f, obj=results)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", help="topic you are intrested in", default="large language model based agents")
    parser.add_argument("--num_results", help="number of papers to find on the topic", default=5)
    args = parser.parse_args()
    scrape_papers(args.topic, int(args.num_results))