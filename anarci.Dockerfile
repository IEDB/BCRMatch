FROM harbor.lji.org/iedb-public/tcrmatch:0.1.1 AS build

# official Miniconda3 base image (Debian 12)
FROM continuumio/miniconda3

RUN mkdir -p /src/bcrmatch && \
    mkdir -p /TCRMatch

COPY --from=build /TCRMatch/tcrmatch /src

# BCRMatch requires TCRMATCH_PATH environment defined
# Must point to folder containing 'tcrmatch' executable
ENV TCRMATCH_PATH=/src

# Create a new conda environment with Python 3.12  
RUN conda create -n myenv python=3.8.10 -y

# '-n': specify conda environment
# '-c': specify channel from which to install the package
RUN conda install -n myenv -c conda-forge biopython -y && \
    conda install -n myenv -c bioconda anarci -y

# BCRMatch utilizes 'libgomp.so.1' shared library that's part of
# the GNU Compiler Collection (GCC)
RUN apt-get update && apt-get install -y libgomp1

WORKDIR /src/bcrmatch

COPY requirements.txt .

# Install packages from requirements.txt using conda
RUN while read requirement; do conda install -n myenv -c conda-forge $requirement -y; done < requirements.txt

COPY . .

RUN bash download-latest-models.sh

# Activate the environment and set it as default  
RUN echo "source activate myenv" > ~/.bashrc  

# Make the environment available in the shell by sourcing the Conda setup
SHELL ["/bin/bash", "-c"]

CMD ["sh", "-c", "python3 run_bcrmatch.py ${BCRMATCH_ARGS}"]