FROM python:3.6

WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt

RUN chgrp -R 0 /code && \
    chmod -R g=u /code

EXPOSE 9090

USER 1000
CMD ["python", "/code/app.py"]