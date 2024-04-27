import pandas as pd
import subprocess

df = pd.read_csv('resource/repo_list_100.csv', header=0)
num_files = []
for index, rows, in df.iterrows():
    path = 'repo/' + rows['name']
    command = "find -type f -name '*.py' | wc -l"
    output = subprocess.run(command.split(), shell=True, cwd=path, capture_output=True, text=True)
    num_files.append(int(output.stdout))
    
df['num_files'] = num_files
df.to_csv('resource/repo_list_100_2.csv', index=False)