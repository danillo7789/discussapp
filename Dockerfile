# Use the desired base Python image
FROM python:3.10.8-alpine

# Set the working directory inside the container
WORKDIR /usr/src/app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system-level dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip

# Copy the requirements.txt file to the container
COPY requirements.txt /usr/src/app/

# Install Python dependencies from requirements.txt
RUN pip install -r requirements.txt

# Copy the entire project to the container (except for files specified in .dockerignore)
COPY . .

# Set executable permission for the entrypoint.sh script
RUN chmod +x entrypoint.sh

# Expose the port on which your Django app listens
EXPOSE 8000

# Set the entry point for the container
ENTRYPOINT ["./entrypoint.sh"]
