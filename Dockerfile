# Use an official Python runtime as the base image
FROM python:3.9-slim

# Install cron
RUN apt-get update && apt-get install -y cron curl zip
# Copy cron config and run it
COPY cronjob.conf /etc/cron.d/cronjob
RUN chmod 0644 /etc/cron.d/cronjob
RUN crontab /etc/cron.d/cronjob

# Set the working directory in the container
WORKDIR /app

# Install AWS CLI
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
RUN rm *.zip

# Install any dependencies if required (e.g., if your script needs additional packages)
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Start cron in the foreground (this keeps the container running)
CMD ["cron", "-f"]

