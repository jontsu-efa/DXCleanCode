# DXPractice
Simple tool to improve and practice developer experience (DX). 

Teachers can create exercises in the tool, which consist of different coding tasks. Each task requires a solution code (in any language) that relates to a specific topic.

## Features of the tool include:

- **Account Management:** Students and teachers can log in and out, as well as create a new account. Username is the user's GitHub handle and role is determined by teacher. Only users who have their GitHub handle whitelisted can create an account. If there are no users or no GitHub handles in the whitleist, the first user to register will become a teacher who can then manage the whitelist.
- **Exercise Catalogue:** Users can view a list of the available exercises in the tool and can access information about each exercise.
- **Coding Practice:** Students can practice their coding skills by providing solutions to the tasks in the exercise. Solutions are managed via GitHub, either by establishing a new repository or generating an issue within an existing repository. The solution's GitHub link is provided to the tool.
- **Peer Review:** The solutions submitted by students are reviewed by other students. Reviews are submitted as issues within GitHub. The review's GitHub link is provided to the tool.
- **Exercise Creation (Teachers only):** Only teachers can create a new exercise by providing the name of the exercise and a list of tasks in text format.
- **Exercise Deletion or Edit (Teachers only):** Only a teacher who has created the exercise can delete or edit the given exercise.

## Testing & Developing

Create a .env file in the root directory of the project and add your secret key and your local database uri:

.env
```bash
SECRET_KEY=your-secret-key
SQLALCHEMY_DATABASE_URI='your-local-database-uri'
```

You can generate a secret key using Python. Open the Python interpreter by typing python or python3 in your terminal, then enter the following commands:

```bash
import os
print(os.urandom(24))
```

It is probably a good idea to create a virtual environment prior to installing dependencies or running the application, so execute the following commands:

```bash
python3 -m venv venv
source venv/bin/activate
```

Create and connect to your database and initialise it by typing the following at the root folder in your terminal:

```bash
psql < schema.sql 
```

To install the necessary dependencies and start the development server, execute the following commands in your terminal. Make sure you are in the root directory of the application:

```bash
pip install -r requirements.txt
flask run
```
