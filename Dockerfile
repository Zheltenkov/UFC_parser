# ufc_parcer/Dockerfile

FROM python:3.9-slim

WORKDIR /ufc_parcer

COPY ./requirements.txt ./requirements.txt

RUN python -m pip install --upgrade pip && pip3 install -r ./requirements.txt

COPY . ./

ENTRYPOINT [ "python3" ]

CMD ["main.py"]