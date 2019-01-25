# skygate-challenge-chapter-1
Solution to challenge from chapter 1. Tested on Windows 10, python 3.6

**How to start:**
1. Clone or download repository
2. Make sure you have Docker(with docker container) and python (it's tested on python 3.6+) installed
3. Run python file 'run_script.py', it's in main folder of repository. It should create docker image and install everything needed to run application. Fixtures for testing are attached in this command. Script should run application on http://127.0.0.1:8000/
4. Now go to http://127.0.0.1:8000/api/exam/exam-sheets/ or http://127.0.0.1:8000/api/exam/exam-tasks/ . To access data you will need to log in. Fixtures contains 5 users with different data. Users(format login:password): admin:testpassword, student1:testpassword , student2:testpassword , teacher1:testpassword, teacher2:testpassword
5. User admin:testpassword has access to http://127.0.0.1:8000/admin

* Endpoints(Views that shows details and list without filtering objects are editable only by owners (other users can only see data)):
    1. Exam Sheets:
        - http://127.0.0.1:8000/api/exam/exam-sheets/ - returns list of exam sheets that logged user owns (request.user=owner), and that are not archived (is_archived=False), POST request creates new object with owner=request.user. Accepts queryparam student which shows list of sheets with given user.
        - http://127.0.0.1:8000/api/exam/exam-sheets/archive - returns list of exam sheets that logged user owns, and that are archived (is_archived=True)
        - http://127.0.0.1:8000/api/exam/exam-sheets/nofilter - returns list of exam sheets without filtering out
        - http://127.0.0.1:8000/api/exam/exam-sheets/1/ - returns details of exam sheet with id=1, owner can update and delete object
        - http://127.0.0.1:8000/api/exam/exam-sheets/1/archive/ - owner can change exam_sheet status is_archived to True/False, when accesing this endpoint
    2. Exam Task:
        - http://127.0.0.1:8000/api/exam/exam-tasks/ - returns list of tasks from exam sheets that user owns. User can create new task and assign it to exam sheet
        - http://127.0.0.1:8000/api/exam/exam-tasks/1/ - returns details of exam task with id=1 . Owner can update and delete object
        - http://127.0.0.1:8000/api/exam/exam-tasks/1/answer - allows student to pass an answer to exam task
        - http://127.0.0.1:8000/api/exam/exam-tasks/1/sheet - returns list of tasks assigned to exam_sheet with id=1

**Alternative way of starting app.**
If you can't use Docker, or Docker settings doesn't work on your machine you can run project in few steps:
1. Create virtualenv with python 3.6+
2. In repository's main folder run: pip install -r requirements.txt
3. Go to src folder
4. Run commands:
- python manage.py migrate 
- python manage.py loaddata basefixture.json &&
- python manage.py runserver