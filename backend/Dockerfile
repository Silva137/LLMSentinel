FROM python:3.10-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# set the working directory in the container
WORKDIR /backend

# copies the requirements file to the container
COPY ./requirements.txt /backend/requirements.txt

# install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# copies the rest of the code to the container
COPY . /backend/

# expose the port 8000 
EXPOSE 8000

# command to run the django server
CMD ["sh", "./entrypoint.sh"]


