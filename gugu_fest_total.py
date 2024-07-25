import subprocess
import os



def run_scripts():
    # 폴더 경로 설정
    folder_path = r'/Users/choejeongho/Desktop/gugu_fest0725'
    
    # 스크립트 파일 이름 생성
    script_names = [f'gugu_festEx{str(i).zfill(2)}.py' for i in range(10)]
    
    # 각 스크립트를 순차적으로 실행
    for script in script_names:
        script_path = os.path.join(folder_path, script)
        try:
            print(f'Running {script}...')
            result = subprocess.run(['python', script_path], check=True, capture_output=True, text=True)
            print(f'Output of {script}:\n{result.stdout}')
        except subprocess.CalledProcessError as e:
            print(f'Error running {script}:\n{e.stderr}')
            break

if __name__ == "__main__":
    run_scripts()
