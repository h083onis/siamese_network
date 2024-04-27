import argparse
from datetime import datetime
from repocollector.github import GithubRepositoriesCollector
import pandas as pd


def collect_repo(args):
    github_crawler = GithubRepositoriesCollector(args.api_token) 

    id = []
    name = []
    url = []
    result = github_crawler.collect_repositories(
                    since=datetime(args.since_year, 12, 31),
                    until=datetime(args.until_year, 12, 31),
                    pushed_after=datetime(args.until_year, 6, 1),
                    min_issues=0,
                    min_releases=0,
                    min_stars=args.min_star,
                    min_watchers=0,
                    primary_language=args.language)
    
    for repo in result:
        id.append(repo['id'])
        name.append(repo['full_name'])
        url.append(repo['url'])
    
    df = pd.DataFrame(
        data={'id': id, 'name': name, 'url': url},
        columns=['id','name','url']
    )
    df.to_csv('resource/repo_list2.csv', index=False)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--api_token', type=str)
    parser.add_argument('--language', type=str, default='python')
    parser.add_argument('--since_year', type=int, default=2015)
    parser.add_argument('--until_year', type=int, default=2020)
    parser.add_argument('--min_star', type=int, default=1000)
    args = parser.parse_args()
    collect_repo(args)
    