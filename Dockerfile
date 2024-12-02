# Use Ubuntu 22.04 as the base image (supports ARM64)
FROM ubuntu:22.04

# Set up noninteractive environment to avoid tzdata prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update and install system dependencies
RUN apt-get update && apt-get install -y \
    clang \
    curl \
    git \
    python3 \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    sudo \
    cmake \
    build-essential \
    libboost-dev \
    libboost-all-dev \
    tzdata

# Install pip and upgrade setuptools
RUN python3 -m pip install --upgrade pip setuptools

# Set environment variable to build with TensorFlow support
ENV OPEN_SPIEL_BUILD_WITH_TENSORFLOW=ON

# Install TensorFlow (ensure the version supports ARM64)
RUN pip3 install tensorflow

# Create directory for OpenSpiel and set as working directory
RUN mkdir /open_spiel
WORKDIR /open_spiel

# Clone the OpenSpiel repository
RUN git clone https://github.com/deepmind/open_spiel.git .

# Run install.sh to install OpenSpiel dependencies
RUN ./install.sh

# Install Python requirements
RUN pip3 install --upgrade -r requirements.txt

# Build OpenSpiel
RUN mkdir build && cd build && \
    cmake -DPython3_EXECUTABLE=$(which python3) -DCMAKE_CXX_COMPILER=$(which clang++) ../open_spiel && \
    make -j$(nproc)

# Set PYTHONPATH to include OpenSpiel directories
ENV PYTHONPATH=${PYTHONPATH}:/open_spiel:/open_spiel/build/python

# Set the working directory to /open_spiel
WORKDIR /open_spiel

# Set the default command to bash
CMD ["bash"]