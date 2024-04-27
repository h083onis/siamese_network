import git
import re
import pandas as pd
import argparse


def is_code_ext(file_path):
    splited_file = file_path.split('.')
    if len(splited_file) >= 2 and splited_file[-1] == 'py':
        return True
    else:
        return False
    
def assing_token(block_lines):
    snippet_list = []
    for line in block_lines:
        if line.strip() == '' or line[1:].strip() == '':
            continue
        if line[0] == '+':
            snippet_list.append('<add> ' + line[1:])
        elif line[0] == '-':
            snippet_list.append('<del> ' + line[1:])
        else:
            snippet_list.append('<ctxt> ' + line)
    return ' '.join(snippet_list)
        
    
def extract_diff(diff_lines, f):
    if is_code_ext(diff_lines[0]) == False:
        return
    diff_lines.append('@@')
    flag = False
    block_lines = []
    pattern = r'@@.*?@@'
    
    for line in diff_lines:
        if line[0:2] == '@@':
            if flag == False:
                result = re.sub(pattern, '', line, count=1)
                block_lines.append(result)
                flag = True
            else:
                snippet = assing_token(block_lines)
                print(snippet.encode('utf-8', 'ignore').decode('utf-8'), file=f)
                block_lines = []
                result = re.sub(pattern, '', line, count=1)
                block_lines.append(result)
        elif flag == True:
            block_lines.append(line)
        else:
            continue
        
def extract_diff_block(commit_list, f):
    flag = False
    diff_lines = []
    commit_list.append('diff\n')
    for line in commit_list:
        if line[0:4] == 'diff':
            if flag == False:
                flag = True
                diff_lines.append(line)
            else:
                extract_diff(diff_lines, f)
                diff_lines = []
                diff_lines.append(line)
        elif flag == True:
            diff_lines.append(line)
        else:
            continue

def collect_snippet(args):
    df = pd.read_csv(args.csv_file, header=0)
    df = df[df['num_files'] >= args.limit]
    name_list = df['name']
    EMPTY_TREE_SHA = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
    with open(args.out_file, 'a', encoding='utf-8') as f:
        for i, name in enumerate(name_list, 1):
            print(str(i) +'/' + str(len(name_list)))
            path = 'repo/'+ name
            repo = git.Repo(path)
            commits = list(repo.iter_commits())
            commits.reverse()
            
            for i, commit in enumerate(commits):
                if not commit.parents:
                    diff = repo.git.diff(EMPTY_TREE_SHA, commit.hexsha)
                else:
                    diff = repo.git.diff(commit.hexsha+'~1', commit.hexsha)
                lines = diff.split('\n')
                extract_diff_block(lines, f)
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv_file', type=str)
    parser.add_argument('--out_file', type=str)
    parser.add_argument('--limit', type=int, default=100)
    args = parser.parse_args()
    collect_snippet(args)