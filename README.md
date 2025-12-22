# Content Management & Sharing Platform (student project)

This is a simple Flask app for a Cloud Computing course final project. It supports:

- User registration and login (very simple, for demo)
- File upload and storage to AWS S3 (uses boto3)
- File listing and search by filename
- Simple versioning: duplicate filenames are renamed to name_v2.ext, name_v3.ext, etc.

Quick start (local dev):

1. Create a virtual environment and install dependencies:

```bash
python -m pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and edit values (or set env vars directly):

```bash
cp .env.example .env
# edit .env with your values
```

3. Run the app:

```bash
python app.py
```

Notes:
- The app will create a local sqlite DB by default if you don't set `SQLALCHEMY_DATABASE_URI`.
- AWS credentials and `S3_BUCKET` should be set when you want to integrate with S3.
- This is a student project. Security, input validation and error handling are intentionally minimal.

Student TODOs / known quirks:
- Some typos exist in the code/comments (intentional for student style).
- No email confirmation on register.
# CloudComputing