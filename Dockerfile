# Use an official Python 3.10 alpine runtime as base
FROM python:3.10-alpine

# Set the labels for this Dockerfile
LABEL author="sarthak@felidaesystems.com"

# Update packages and install dependencies
# binutils is required by pyinstaller, it is installed before requirements.txt
# in context of improving the caching facility of docker builds
RUN apk install update
RUN apk add binutils                                        

# Create a new directory inside container that will house your source code and
# set that as your working directory
WORKDIR /pluxsim

# Copy the source code from host current directory (where this Dockerfile is) to 
# container's work directory.
COPY . .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Build the application binaries and install required dependencies.
RUN pyinstaller --specpath 'out/obj' --workpath 'out/obj' --distpath 'out/bin' --noconfirm --onedir --console --name 'pluxsim' --clean 'source/__main__.py'

# Expose the port for application
EXPOSE 11204

# Run the application
CMD ["out/bin/pluxsim/pluxsim", "--config", "config/pluxsim.local.config.jsonc", "--logdir", "out/logs", "--stdout", "--loglvl", "0"]