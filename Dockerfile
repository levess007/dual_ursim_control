FROM python:3.9

ADD dual_ursim_control requirements.txt /dual_ursim_control/
WORKDIR /dual_ursim_control/

RUN pip3 install -r requirements.txt

ARG RELEASE_ID
ENV RELEASE_ID ${RELEASE_ID:-""}

CMD ["python3", "main.py"]