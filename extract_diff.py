import time
import sys
import json
import subprocess
from git import Repo
from gitdb.exc import BadName
import argparse
import pandas as pd
from utils import out_code_dict, out_txt

def is_auth_ext(file_path, auth_ext):
    splited_file = file_path.split('.')
    if len(splited_file) >= 2 and splited_file[-1].lower() in auth_ext:
        return True
    else:
        return False
    

def diff_texts(codes_dict):
    command = 'diff -B -w -u -0 ../resource/pre_process_data/before.txt ../resource/pre_process_data/after.txt'
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output = process.communicate()[0]
    code_dict = out_code_dict(output.decode('utf-8','ignore'))
    codes_dict['added_code'].extend(code_dict['added_code'])
    codes_dict['deleted_code'].extend(code_dict['deleted_code'])
    return codes_dict
        
        
def print_code(repo, hexsha, filepath, ext, type):
    if type == 'before':
        output = repo.git.show(hexsha+"~1"+':'+filepath)
    else:
        output = repo.git.show(hexsha+':'+filepath)
    output = exclude_comment(output, ext)
    out_txt('../resource/pre_process_data/'+type+'.txt', output)


def pipe_process(repo, commit, hexsha, params, commit_dict, type):
    auth_ext = params.auth_ext.split(',')
    if type == 'first':
        for filepath in commit.stats.files:
            if is_auth_ext(filepath, auth_ext) == False:
                continue
            ext = filepath.split('.')[-1].lower()
            codes_dict = {}
            codes_dict['filepath'] = filepath
            codes_dict['added_code'] = []
            codes_dict['deleted_code'] = []
            with open('../resource/pre_process_data/before.txt','w', encoding='utf-8') as f:
                f.truncate(0)
            print_code(repo, hexsha, filepath, ext, type='after')
    
            codes_dict = diff_texts(codes_dict)
            if codes_dict['added_code'] == [] and codes_dict['deleted_code'] == []:
                continue
            commit_dict['codes'].append(codes_dict)
    
    else:
        diff = commit.diff(hexsha)
        for item in diff:
            if is_auth_ext(item.b_path, auth_ext) == False:
                continue
            ext = item.b_path.split('.')[-1].lower()
            codes_dict = {}
            codes_dict['filepath'] = item.b_path
            codes_dict['added_code'] = []
            codes_dict['deleted_code'] = []
            # print(item.b_path)
            ch_type = item.change_type
            if ch_type == 'M' or ch_type == 'R':
                print_code(repo, hexsha, item.a_path, ext, type='before')
                print_code(repo, hexsha, item.b_path, ext, type='after')
            elif ch_type == 'A' or ch_type == 'C':
                with open('../resource/pre_process_data/before.txt','w', encoding='utf-8') as f:
                    f.truncate(0)
                print_code(repo, hexsha, item.b_path, ext, type='after')
            else:
                continue
            
            codes_dict = diff_texts(codes_dict)
            if codes_dict['added_code'] == [] and codes_dict['deleted_code'] == []:
                continue
            commit_dict['codes'].append(codes_dict)

    return commit_dict

def excute(params):
    code_snippet = []
    df = pd.read_csv(params.csv_filename, header=0)
    repo_list = list(df['name'])
    code_snippet = []
    for repo_name in repo_list:
        repo = Repo('repo/'+repo_name)
        head = repo.head
    
        if head.is_detached:
            pointer = head.commit.hexsha
        else:
            pointer = head.reference
            
        commits = list(repo.iter_commits(pointer))
        commits.reverse()
        commit_list = []
        for i, item in enumerate(commits):
            commit_dict = {}
            commit_dict['commit_id'] = item.hexsha
            commit = repo.commit(item.hexsha)
            commit_dict['timestamp'] = commit.authored_date
            commit_dict['msg'] = commit.message
            commit_dict['codes'] = []
            print(i, item.hexsha)
            try:
                commit = repo.commit(item.hexsha+'~1')
                pipe_process(repo, commit, item.hexsha, params, commit_dict, type='normal')
            except (IndexError, BadName):   
                pipe_process(repo, commit, item.hexsha, params, commit_dict, type='first')
            commit_list.append(commit_dict)
   
        
    with open(params.json_name, 'w') as f:
        json.dump(commit_list, f, indent=2)

    
  
def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-csv_file', type=str)
    parser.add_argument('-out_file', type=str)
    parser.add_argument('-limit', type=int, default=5)
    parser.add_argument('-auth_ext', type=str, default='py')
    return parser


if __name__ == '__main__':
    params = read_args().parse_args()
    excute(params)
    sys.exit(0)