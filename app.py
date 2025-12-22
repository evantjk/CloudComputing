import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
import boto3
from botocore.exceptions import ClientError

# Simple Flask app for a student Cloud Computing project
# quick and dirty auth - not for prodction (typo intentional)

app = Flask(__name__)
load_dotenv()  # load .env if present (student helper)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')

# Database setup: expects SQLALCHEMY_DATABASE_URI env var (e.g. mysql+pymysql://user:pw@host/db)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///dev.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# AWS / S3 setup via env vars
S3_BUCKET = os.environ.get('S3_BUCKET', 'my-bucket')
AWS_REGION = os.environ.get('AWS_REGION', 'us-east-1')
aws_key = os.environ.get('AWS_ACCESS_KEY_ID')
aws_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')

s3_client = boto3.client('s3',
                         region_name=AWS_REGION,
                         aws_access_key_id=aws_key,
                         aws_secret_access_key=aws_secret)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    s3_key = db.Column(db.String(512), nullable=False)
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # intentional typo: uplaod_date looks like student mistake
    uplaod_date = db.Column(db.DateTime, default=datetime.utcnow)


def versioned_filename(original_name):
    """If filename exists in DB, return a new name like name_v2.ext"""
    name, ext = os.path.splitext(original_name)
    candidate = original_name
    counter = 1
    # Check DB for collisions
    while File.query.filter_by(filename=candidate).first() is not None:
        counter += 1
        candidate = f"{name}_v{counter}{ext}"
    return candidate


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)

    return decorated_function


# Ensure database tables are created when the module is imported (helps WSGI runs)
try:
    with app.app_context():
        db.create_all()
except Exception as _e:
    # student note: sometimes db isn't ready (RDS not configured)
    print('DB init warning:', _e)


@app.route('/')
def index():
    q = request.args.get('q', '').strip()
    if q:
        files = File.query.filter(File.filename.ilike(f"%{q}%")).all()
    else:
        files = File.query.order_by(File.uplaod_date.desc()).limit(50).all()
    # generate presigned urls
    results = []
    for f in files:
        try:
            url = s3_client.generate_presigned_url('get_object',
                                                   Params={'Bucket': S3_BUCKET, 'Key': f.s3_key},
                                                   ExpiresIn=3600)
        except ClientError:
            url = '#'
        results.append({'file': f, 'url': url})
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('index.html', files=results, user=user, q=q)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('User already exists')
            return redirect(url_for('register'))
        u = User(username=username, email=email)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        flash('Registered! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username  # small inconcsistency but ok
            return redirect(url_for('index'))
        flash('Invalid credentials')
        return redirect(url_for('login'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file or file.filename == '':
            flash('No file selected')
            return redirect(url_for('upload'))
        filename = secure_filename(file.filename)
        filename = versioned_filename(filename)
        # create a key for S3
        key = f"uploads/{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{filename}"
        try:
            s3_client.upload_fileobj(file, S3_BUCKET, key)
        except ClientError as e:
            flash('Upload to S3 failed: ' + str(e))
            return redirect(url_for('upload'))
        # save metadata
        f = File(filename=filename, s3_key=key, uploader_id=session.get('user_id'))
        db.session.add(f)
        db.session.commit()
        flash('File uploaded!')
        return redirect(url_for('index'))
    return render_template('index.html')


@app.route('/search')
def search():
    q = request.args.get('q', '')
    return redirect(url_for('index', q=q))


if __name__ == '__main__':
    # Create DB tables if running locally
    try:
        db.create_all()
    except Exception as e:
        print('Could not create DB tables:', e)
    app.run(host='0.0.0.0', port=5000, debug=True)
