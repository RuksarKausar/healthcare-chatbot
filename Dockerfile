FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "-c", "import subprocess; import sys; p1=subprocess.Popen([sys.executable, '-m', 'rasa', 'run', '--enable-api', '--cors', '*', '--port', '5005']); p2=subprocess.Popen([sys.executable, 'webhook_server.py']); p1.wait()"]
