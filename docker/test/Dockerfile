FROM python:3.7-alpine AS base
WORKDIR /code
RUN apk add --no-cache gcc musl-dev linux-headers git tree
COPY docker/requirements.txt .
RUN pip install -r requirements.txt

FROM base AS src_remote
RUN git clone --depth=1 -b master https://github.com/theme-ontology/tstp /code/tstp
RUN git clone --depth=1 -b master https://github.com/theme-ontology/theming /code/theming

FROM src_remote AS src_local
COPY . /code/tstpdev
COPY docker/credentials.py /code/tstpdev/pylib
COPY docker/credentials.py /code/tstp/pylib
RUN pwd
RUN ls -la
RUN tree -L 2

FROM src_remote AS final
EXPOSE 31985
ENTRYPOINT [ "sh", "/code/tstpdev/scripts/dockerstartup.sh" ]
