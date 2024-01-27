import argparse
from scrape import scrape_papers
from build_connection import build_connection_graph
import shutil
import datetime

# import nltk
# nltk.download("stopwords")
# nltk.download("punkt")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument("--topic", help="topic you are intrested in", default="large language model based agents")
#     parser.add_argument("--num_results", help="number of papers to find on the topic", default=5)
#     args = parser.parse_args()

def create_connection_plot(topic, num_results):
    nw = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')[:-3]
    output_dir = f"../artifacts/{nw}"
    relations = scrape_papers(topic, num_results, output_dir)
    return build_connection_graph(relations, output_dir)