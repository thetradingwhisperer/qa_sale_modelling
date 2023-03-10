FROM python:3.10.6



WORKDIR /repo

COPY requirements.txt ./

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#CMD [ "python", "./your-daemon-or-script.py" ]