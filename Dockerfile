# Use an official Python runtime as the base image
FROM python:3.11-slim

# Set environment variables to prevent Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install sudo and other necessary packages
RUN apt-get update && apt-get install -y sudo

# Upgrade pip
RUN pip install --upgrade pip

# Set the working directory in the container
WORKDIR /lb

# Copy all files from the current directory to /lb in the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Add a non-root user for security
RUN addgroup --system lbgroup && adduser --system lbuser --ingroup lbgroup

# Add lbuser to the sudoers file with no password required
RUN echo "lbuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Change ownership of the working directory to lbuser
RUN chown -R lbuser:lbgroup /lb

# Switch to the non-root user
USER lbuser

# Expose the port the app runs on
EXPOSE 80

# Define the default command to run the application with sudo
CMD ["python3", "lb.py"]
