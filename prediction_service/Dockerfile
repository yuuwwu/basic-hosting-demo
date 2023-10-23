FROM python:3.10.13-slim-bullseye

# he official Debian/Ubuntu docker image automatically removes the cache by default
# Removing the docker-clean file mitigates that issue
RUN rm -rf /etc/apt/apt.conf.d/docker-clean

# Install and config locales for onnxruntime
RUN apt-get update && apt-get install -y locales locales-all

ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8
RUN locale-gen en_US.UTF-8
RUN dpkg-reconfigure locales

COPY . app/
WORKDIR app/

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["uvicorn", "prediction_service.service:app", "--host", "0.0.0.0", "--port", "8080"]
