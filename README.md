How to Run the Project
Follow these steps to deploy and run the application on your AWS EC2 server.

1. Prerequisites
An active AWS EC2 Instance (Ubuntu)

Your Private Key file (cloud-project-key (1).pem)

An RDS MySQL Database and S3 Bucket

2. Installation & Deployment
Step 1: Connect to your EC2 Server Open your terminal (Command Prompt or PowerShell) and run the following command:

ssh -i "C:\Users\User\Downloads\cloud-project-key (1).pem" ubuntu@13.219.228.129

Step 2: Clone the repository Once logged in to the server, download the application code:

git clone https://github.com/evantjk/CloudComputing.git
cd CloudComputing

Step 3: Install dependencies Install the required Python libraries:

sudo apt update
sudo apt install python3-pip python3-venv -y
pip3 install -r requirements.txt --break-system-packages

3. Secure Configuration
The application requires your specific cloud credentials to function.

Type "nano" in cmd

Step 2: Paste your configuration Copy the text below and paste it into the file:


FLASK_SECRET: A random string for session security (e.g., supersecretkey). For security purpose , please refer information via word file.
SQLALCHEMY_DATABASE_URI:
For Cloud/Production: Use your RDS MySQL connection string: mysql+pymysql://admin:PASSWORD@ENDPOINT:3306/cloudproject
S3_BUCKET: The name of your AWS S3 bucket for file storage.
AWS_REGION: Your AWS region (e.g., us-east-1).
AWS_ACCESS_KEY_ID: Your AWS IAM Access Key.
AWS_SECRET_ACCESS_KEY: Your AWS IAM Secret Key.

Step 3: Save and Exit

Press Ctrl + X

Press Y (to say Yes)

Press Enter (to save)

python3 app.py

Access the Website: Open your browser and go to http://13.219.228.129:5000

