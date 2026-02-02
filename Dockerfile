# TODO: Change to an officially released version of Python before deploying to production.
ARG PYTHON_VERSION=3.13-slim

FROM python:${PYTHON_VERSION}

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN mkdir -p /code

WORKDIR /code

RUN pip install pipenv
COPY Pipfile Pipfile.lock /code/
RUN pipenv install --deploy --system
COPY . /code

ENV SECRET_KEY "1bXwjSyVAJ3kSTWAhxHn4ngVQr2BgLg6XOsLlGWSLoSMCoc2UJ"
RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn","--bind",":8000","--workers","2","flight_prediction.wsgi"]
