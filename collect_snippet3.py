import git
import re
import pandas as pd
import argparse
import codecs
import subprocess

def is_code_ext(file_path):
    splited_file = file_path.split('.')
    if len(splited_file) >= 2 and splited_file[-1] == 'py':
        return True
    else:
        return False
    
def assing_token(block_lines):
    snippet_list = []
    for line in block_lines:
        if line.strip() == '':
            continue
        if line[0] == '+':
            snippet_list.append('<add> ' + line[1:])
        elif line[0] == '-':
            snippet_list.append('<del> ' + line[1:])
        else:
            snippet_list.append('<ctxt> ' + line)
    return ' '.join(snippet_list)
        
    
def extract_diff(diff_lines, diff_blocks):
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
                txt = assing_token(block_lines)
                diff_blocks.append(txt)
                block_lines = []
                result = re.sub(pattern, '', line, count=1)
                block_lines.append(result)
        elif flag == True:
            block_lines.append(line)
        else:
            continue

               
def extract_diff_block(commit_list):
    commit_list = [line.strip() for line in commit_list if line.strip() != '']
    flag = False
    diff_lines = []
    diff_blocks = []
    commit_list.append('diff\n')
    for line in commit_list:
        if line[0:4] == 'diff':
            if flag == False:
                flag = True
                diff_lines.append(line)
            else:
                extract_diff(diff_lines, diff_blocks)
                diff_lines = []
                diff_lines.append(line)
        elif flag == True:
            diff_lines.append(line)
        else:
            continue
    return ' <sep> '.join(diff_blocks)


def collect_snippet(args):
    df = pd.read_csv(args.csv_file, header=0)
    name_list = df['name']
    with open(args.out_file, 'a') as f_out:
        for i, name in enumerate(name_list, 1):
            print(str(i) +'/' + str(len(name_list)))
            path = 'repo/'+ name
            # r = git.Repo(path)
            git_log_command = ['git', 'log', '-p']
            with open('tmp.txt', 'w', encoding='utf-8') as f_tmp:
                f_tmp.truncate(0)
                f_tmp.seek(0)
                subprocess.run(git_log_command, cwd=path, stdout=f_tmp, shell=True)
            with codecs.open('tmp.txt', 'r', encoding='utf-8', errors='ignore') as f_tmp:
                commit_list = []
                flag = False
                while True:
                    line = f_tmp.readline()
                    if line == '':
                        commit_snippet = extract_diff_block(commit_list)
                        if commit_snippet != '' and commit_snippet.isascii():
                            print(commit_snippet.encode('utf-8', 'ignore').decode('utf-8'), file=f_out)
                        break
                    if line[0:6] == 'commit':
                        if flag == False:
                            flag = True
                            commit_list.append(line)
                        else:
                            commit_snippet = extract_diff_block(commit_list)
                            if commit_snippet != '' and commit_snippet.isascii():
                                print(commit_snippet.encode('utf-8', 'ignore').decode('utf-8'), file=f_out)
                            commit_list = []
                            commit_list.append(line)
                    else:
                        commit_list.append(line)
            # break
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv_file', type=str)
    parser.add_argument('--out_file', type=str)
    args = parser.parse_args()
    collect_snippet(args)