FROM python:3.6

RUN adduser node root

RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt

RUN chmod -R 775 /code
RUN chown -R node:root /code

EXPOSE 9090

USER 1000
CMD ["python", "/code/app.py"]