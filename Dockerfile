FROM python:3.9

ADD requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ADD dual_ursim_control /dual_ursim_control/
WORKDIR /dual_ursim_control/

ARG RELEASE_ID
ENV RELEASE_ID ${RELEASE_ID:-""}

EXPOSE 8888/tcp

CMD ["python3", "main.py"]