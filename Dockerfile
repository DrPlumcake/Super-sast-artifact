# FROM super-sast, copy-paste the Dockerfile is better?

FROM ghcr.io/par-tec/super-sast:20231115-108-746a559 as super-sast

FROM docker.io/library/python:3.11.1-alpine as base_python
COPY --from=super-sast / /

# RUN apt-get update
COPY main.py /
COPY entrypoint.sh /
COPY sast_to_log.py /

RUN mkdir parse_scripts
COPY parse_scripts/* /parse_scripts
COPY request.py /

RUN chmod +x /entrypoint.sh
RUN chmod +x /sast_to_log.py
RUN chmod +x /main.py

# Since this is a job container, we don't need an healthcheck.
HEALTHCHECK NONE
ENTRYPOINT ["/entrypoint.sh"]
