FROM python:3

ADD ambrosia.py /
ADD google_maps_api.py /

COPY ./requirements.txt ./

RUN pip install -r ./requirements.txt

CMD [ "python", "-u", "./ambrosia.py"]