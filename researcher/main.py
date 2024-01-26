import argparse
from scrape import scrape_papers
from citation_plotting import create_citation_plot
import shutil
import datetime

# import nltk
# nltk.download("stopwords")
# nltk.download("punkt")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", help="topic you are intrested in", default="large language model based agents")
    parser.add_argument("--num_results", help="number of papers to find on the topic", default=5)
    args = parser.parse_args()
    nw = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')[:-3]
    output_dir = f"../artifacts/{nw}"
    relations = scrape_papers(args.topic, int(args.num_results), output_dir)
    create_citation_plot(relations, output_dir)