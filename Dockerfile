FROM harbor.lji.org/iedb-public/tcrmatch:0.1.1

# Prevent python from writing bytcode files to disk
ENV PYTHONDONTWRITEBYTECODE 1

# Send stdout/stderr streams straight to termainl
ENV PYTHONUNBUFFERED 1

# Set path to TCRMatch, which is required to run BCRMatch
ENV TCRMATCH_PATH=/TCRMatch

RUN apt update && \
    apt install -y wget make && \
    apt-get update && \
    apt-get install -y python3-pip && \
    apt-get install -y build-essential vim && \
    pip install --upgrade setuptools pip && \
    echo 'alias python="python3"' >> ~/.bashrc

RUN apt-get install ca-certificates -y && \
    wget https://cacerts.digicert.com/GeoTrustRSACA2018.crt.pem -O /usr/local/share/ca-certificates/GeoTrustRSACA2018.crt && \
    wget https://cacerts.digicert.com/DigiCertGlobalRootCA.crt.pem -O /usr/local/share/ca-certificates/DigiCertGlobalRootCA.crt && \
    update-ca-certificates

RUN mkdir -p /src/bcrmatch

WORKDIR /src/bcrmatch

COPY . ./

RUN pip install -r requirements.txt

CMD ["tail", "-f", "/dev/null"]