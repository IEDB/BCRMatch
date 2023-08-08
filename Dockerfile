FROM python:3.10

LABEL maintainer="hkim@lji.org"

RUN apt update && \
    apt install -y wget make && \
    apt-get install -y build-essential vim

RUN pip install --upgrade setuptools pip

RUN apt-get install ca-certificates -y && \
    wget https://cacerts.digicert.com/GeoTrustRSACA2018.crt.pem -O /usr/local/share/ca-certificates/GeoTrustRSACA2018.crt && \
    wget https://cacerts.digicert.com/DigiCertGlobalRootCA.crt.pem -O /usr/local/share/ca-certificates/DigiCertGlobalRootCA.crt && \
    update-ca-certificates

RUN mkdir -p /src/bcrmatch

WORKDIR /src/bcrmatch

COPY . ./

RUN pip install -r requirements.txt

CMD ["tail", "-f", "/dev/null"]