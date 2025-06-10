FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update -y && apt-get upgrade -y
RUN apt-get install -y binutils libproj-dev gdal-bin
RUN apt-get install -y libgl1-mesa-glx libreoffice tzdata 
RUN ln -snf /usr/share/zoneinfo/Asia/Seoul /etc/localtime

WORKDIR /usr/src/app
COPY ./ /usr/src/app/
RUN pip install --upgrade pip setuptools
RUN pip install --no-cache-dir -r requirements.txt