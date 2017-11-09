FROM python:2.7

WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt

RUN chgrp -R 0 /code && \
    chmod -R g=u /code

WORKDIR /.validium
RUN chgrp -R 0 /.validium && \
    chmod -R g=u /.validium

EXPOSE 9090

USER 1000
CMD ["python", "/code/app.py"]
