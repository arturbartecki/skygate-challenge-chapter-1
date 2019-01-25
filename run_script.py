import os


def docker_run_app(command):
    return os.system(f'docker-compose run app sh -c {command}')


def main():
    os.system('docker-compose build')
    docker_run_app('"python manage.py migrate"')
    docker_run_app('"python manage.py loaddata basefixture.json"')
    os.system('docker-compose up')
    
if __name__ == '__main__':
    main()