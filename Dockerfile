# Start from the latest python base image
FROM python:3

# Set workspace
WORKDIR /src

#Copy the code into the conatiner
COPY /src .

# Define environment veriables
ENV TZ="America/London"
ENV username="my@email.address"
ENV watch-interval=3600

#Expose the nessasary volumes
VOLUME /photos

# Expose port 8080 to the outside world
EXPOSE 8080

# Create health check to check / url
HEALTHCHECK --interval=5m --timeout=3s --start-period=10s --retries=3 CMD curl -f http://localhost:8080/ || exit 1

# Command to run the executable
CMD [ "python3", "-u", "./src/main.py" ]