FROM harbor.lji.org/iedb-public/tcrmatch:1.0.2 AS build

# official Miniconda3 base image (Debian 12)
FROM continuumio/miniconda3

RUN mkdir -p /src/bcrmatch && \
    mkdir -p /TCRMatch

COPY --from=build /TCRMatch/tcrmatch /src

# BCRMatch requires TCRMATCH_PATH environment defined
# Must point to folder containing 'tcrmatch' executable
ENV TCRMATCH_PATH=/src

# Create a new conda environment with Python 3.8.10  
RUN conda create -n myenv python=3.8.10 -y

# '-n': specify conda environment
# '-c': specify channel from which to install the package
RUN conda install -n myenv -c conda-forge biopython -y && \
    conda install -n myenv -c bioconda anarci hmmer -y

# BCRMatch utilizes 'libgomp.so.1' shared library that's part of
# the GNU Compiler Collection (GCC)
RUN apt-get update && apt-get install -y libgomp1

WORKDIR /src/bcrmatch

COPY requirements.txt .

# Install packages from requirements.txt using pip in the conda environment
RUN /opt/conda/envs/myenv/bin/pip install -r requirements.txt

COPY . .

RUN /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate myenv && bash download-latest-models.sh"

ENV CONTAINER_TYPE=anarci

# Use the direct path to Python in the conda environment
CMD ["/bin/bash", "-c", "source /opt/conda/etc/profile.d/conda.sh && conda activate myenv && cd /src/bcrmatch && python run_bcrmatch.py ${BCRMATCH_ARGS}"]