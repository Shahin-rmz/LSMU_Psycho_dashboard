FROM python:3.8
ENV PYTHONUNBUFFERED 1

RUN apt-get update
RUN apt-get install -y git curl gnupg binutils libproj-dev gdal-bin gettext postgresql-client supervisor

RUN pip install --no-cache-dir -U pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get remove git -y
RUN apt-get autoremove -y
RUN apt-get clean
ENV C_FORCE_ROOT=1
COPY . /code
RUN rm -rf .git
WORKDIR /code
RUN mkdir logs
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord"]
