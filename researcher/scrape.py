import arxiv
import os
import json
import nltk
from rake_nltk import Rake
import fitz
from PIL import Image, ImageDraw
import re
from tqdm import tqdm


def refine_query(query):
    rake = Rake()
    rake.extract_keywords_from_text(query)
    keywords = rake.get_ranked_phrases()
    return " ".join(keywords)


def get_links(page):
    cites = []
    external_links = []
    link = page.first_link
    while link: # iterate over the links on page
        # do something with the link, then:
        if 'cite' in str(link.uri):
            cites.append(link.uri)
        elif link.is_external:
            external_links.append(link.uri)
        link = link.next
    return list(set(cites)), list(set(external_links))
    
def get_figures(page):
    # issue with plotting the size of plot doesnot match size of figure
    zoom = 2
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    fig = page.get_drawings()
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    draw = ImageDraw.Draw(img)
    for fg in fig:
        rect = fg['rect']
        rect = [rect[0]*img.width, rect[1]*img.height, rect[2]*img.width, rect[3]*img.height]
        rect = [x/1000 for x in rect]
        draw.rectangle(rect, outline='red', width=2)
    return img

def extract_features_from_pdf(pdfilepath):
    doc = fitz.open(pdfilepath)
    count = 0
    # Count variable is to get the number of pages in the pdf
    for p in doc:
        count += 1
    
    matches = []
    cites = []
    links = []
    for i in tqdm(range(count)):
        page = doc.load_page(i)
        
        text = page.get_text()
        # does this page has refrence
        match = re.findall(pattern='arXiv:[0-9.]+', string=text)
        # 6 to get rid of arXiv and id is of 9 digits
        match = [x[6:][:9] for x in match]

        # get cited page and extranal links like github or blog posts
        cites, links = get_links(page)

        # find digrams on the image, plot, save
        # img = get_figures(page)
        # img.save(f"{pdfilepath[:-4]}/imgs/{val}")
        matches+= match
        cites += cites
        links += links
    doc.close()
    return matches, cites, links

def extract_features_from_arxiv(p):
    title = p.title
    summary = p.summary

    if p.comment:
        conference = "".join(p.comment.split()[-2])
    else:
        conference = None
    return (title, conference, summary)

def scrape_papers(query, numresults , output_dir):
    refined_query = refine_query(query)
    os.makedirs(output_dir, exist_ok=True)
    results = []

    search = arxiv.Search(
        query=refined_query,
        max_results=numresults,
        sort_by=arxiv.SortCriterion.Relevance,
    )
    papers = list(search.results())

    results = []
    relations = []

    for i, p in tqdm(enumerate(papers)):
        id = str(p).split('/')[-1][:9]
        file_path = f"{output_dir}/{id}.pdf"
        p.download_pdf(filename=file_path)
        title, conference, summary = extract_features_from_arxiv(p)
        related_paper_ids, cites, links = extract_features_from_pdf(file_path)
        res = {}
        res['title'] = title
        res['conference'] = conference
        res['summary'] = summary
        res['related_papers'] = related_paper_ids
        res['cites'] = cites
        res['links'] = links
        results.append(res)
        relations.append({f'{id}':related_paper_ids})
    
    with open(f'{output_dir}/result.json', 'w') as f:
        json.dump(fp=f, obj=results)
    return relations