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

# Command to run the executable
CMD [ "python3", "-u", "./src/main.py" ]