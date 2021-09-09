FROM python:3.9.5
LABEL maintainer="sjavaid"

COPY ./techtrends /techtrends_app
WORKDIR /techtrends_app
RUN pip install -r requirements.txt

# initialize DB with pre-defined posts
RUN python ./init_db.py

# expose port
expose :3111

# command to run on container start
CMD [ "python", "app.py" ]
