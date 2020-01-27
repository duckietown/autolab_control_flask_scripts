# parameters
ARG REPO_NAME="dt-autolab-api"

# ==================================================>
# ==> Do not change this code
ARG ARCH=arm32v7
ARG MAJOR=daffy
ARG BASE_TAG=${MAJOR}-${ARCH}
ARG BASE_IMAGE=dt-commons

# define base image
FROM duckietown/${BASE_IMAGE}:${BASE_TAG}

# check REPO_NAME
ARG REPO_NAME
RUN bash -c \
  'if [ "${REPO_NAME}" = "<REPO_NAME_HERE>" ]; then \
    >&2 echo "ERROR: You need to change the value of REPO_NAME inside Dockerfile."; \
    exit 1; \
  fi'

# define repository path
ARG REPO_PATH="${SOURCE_DIR}/${REPO_NAME}"
WORKDIR "${REPO_PATH}"

# create repo directory
RUN mkdir -p "${REPO_PATH}"

# copy dependencies (APT)
COPY ./dependencies-apt.txt "${REPO_PATH}/"

# install apt dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    $(awk -F: '/^[^#]/ { print $1 }' dependencies-apt.txt | uniq) \
  && rm -rf /var/lib/apt/lists/*

# copy dependencies (PIP3)
COPY ./dependencies-py3.txt "${REPO_PATH}/"

# install python dependencies
RUN pip3 install -r ${REPO_PATH}/dependencies-py3.txt

# copy the source code
COPY ./code/. "${REPO_PATH}/"

# copy avahi services
COPY ./assets/avahi-services/. /avahi-services/

# define launch script
COPY ./launch.sh "${REPO_PATH}/"
ENV LAUNCHFILE "${REPO_PATH}/launch.sh"

# define command
CMD ["bash", "-c", "${LAUNCHFILE}"]

# store module name
LABEL org.duckietown.label.module.type "${REPO_NAME}"
ENV DT_MODULE_TYPE "${REPO_NAME}"

# store module metadata
ARG ARCH
ARG MAJOR
ARG BASE_TAG
ARG BASE_IMAGE
LABEL org.duckietown.label.architecture "${ARCH}"
LABEL org.duckietown.label.code.location "${REPO_PATH}"
LABEL org.duckietown.label.code.version.major "${MAJOR}"
LABEL org.duckietown.label.base.image "${BASE_IMAGE}:${BASE_TAG}"
# <== Do not change this code
# <==================================================

# configure avahi
RUN touch /etc/avahi/avahi-daemon.conf \
  && sed -i 's/#enable-dbus=yes/enable-dbus=no/g' /etc/avahi/avahi-daemon.conf \
  && sed -i 's/#disable-publishing=no/disable-publishing=yes/g' /etc/avahi/avahi-daemon.conf

# TEMPORARY: copy device-list
COPY assets/device_list.txt /static/device_list.txt

# copy docker binary
COPY assets/docker/${ARCH}/docker /bin/docker

# setup duckietown-shell
# TODO: switch back to daffy once merged
RUN dts --set-version daffy-aido-ttic exit

# install ipfs
ARG IPFS_VERSION=0.4.22
ARG IPFS_URL="https://dist.ipfs.io/go-ipfs/v${IPFS_VERSION}/go-ipfs_v${IPFS_VERSION}_linux-${ARCH}.tar.gz"
RUN \
  cd /tmp \
  && wget -O ./go-ipfs.tar.gz ${IPFS_URL} \
  && tar xvfz ./go-ipfs.tar.gz \
  && cd go-ipfs \
  && ./install.sh \
  && cd /tmp \
  && rm -rf ./go-ipfs.tar.gz go-ipfs

# maintainer
LABEL maintainer="Andrea F. Daniele (afdaniele@ttic.edu)"