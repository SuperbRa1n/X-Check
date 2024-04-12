import subprocess
import os
# 获取当前目录的绝对路径
file_path = os.path.abspath(os.path.dirname(__file__))
print(file_path)

def check(repo_name: str, file_name: str) -> dict:
    score_dict = {}
    
    # 与进程进行交互
    os.chdir(file_path)
    input_list = os.listdir(f'{file_path}/input')
    for file in input_list:
        with open(f'{file_path}/input/{file}', 'r') as f:
            input_data = f.read()
        # 启动可执行文件
        os.chdir(f'{file_path}/../{repo_name}')
        if os.path.exists(f'{file_path}/../{repo_name}/bin'):
            os.chdir(f'{file_path}/../{repo_name}/bin')
            if not os.path.exists(file_name):
                score_dict['error'] = '未生成可执行文件，请检查CMakeLists.txt是否正确'
                return score_dict
        else:
            score_dict['error'] = '未找到bin文件夹，请检查工程格式是否正确'
            return score_dict
        process = subprocess.Popen(f"{file_path}/../{repo_name}/bin/{file_name}", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        process.stdin.write(input_data)
        process.stdin.flush()
        stdout, stderr = process.communicate()
        stdout = stdout.replace(' ', '').replace('\n', '')
        os.chdir(file_path)
        if stderr:
            print(stderr)
            score_dict['error'] = stderr
        else:
            with open(f'{file_path}/output/{file}', 'r') as f:
                correct_output = f.read()
            correct_output = correct_output.replace(' ', '').replace('\n', '')
            print('Output:', stdout)
            print('Correct:', correct_output)
            if stdout == correct_output:
                print('Correct')
                score_dict[file.split('.')[0][:-2]] = int(file.split('.')[0][-2:])
                
            else:
                print('Wrong')
                score_dict[file.split('.')[0][:-2]] = 0
        # 等待进程结束
        process.wait()
    return score_dict
