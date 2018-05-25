FROM python

RUN mkdir -p /usr/src/dash-manager
WORKDIR /usr/src/dash-manager

COPY requirements.txt /usr/src/dash-manager
RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/src/dash-manager
