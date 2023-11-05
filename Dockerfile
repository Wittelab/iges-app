FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common

COPY / /app
WORKDIR /app

#RUN  apt-get update && apt-get install -y git
#RUN git clone https://github.com/streamlit/streamlit-example.git .
RUN pip3 install -r requirements.txt

EXPOSE 8080
HEALTHCHECK CMD curl --fail http://localhost:8080/_stcore/health

ENTRYPOINT ["streamlit", "run", "Display.py", "--server.port=8080", "--server.address=0.0.0.0"]

# For google artifact deployment
# docker build --platform linux/amd64 -t iges-app:latest .
# docker tag iges-app:latest us-east4-docker.pkg.dev/som-wittelab-red/iges-app/iges-app:latest
# docker push us-east4-docker.pkg.dev/som-wittelab-red/iges-app/iges-app:latest


# docker tag iges-app:latest ccario83/iges-app:latest
# docker push ccario83/iges-app:latest


# docker tag iges-app:latest us-east4-docker.pkg.dev/wittelab/iges-app/iges-app:latest
# docker push us-east4-docker.pkg.dev/wittelab/iges-app/iges-app:latest