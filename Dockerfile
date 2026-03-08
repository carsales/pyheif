ARG LIBHEIF_VERSION=1.21.2
ARG PYTHON_VERSION=cp312-cp312

# -------------------------------- base ------------------------------------------------
FROM quay.io/pypa/manylinux_2_28:2026.02.06-1 AS base

WORKDIR /build

RUN dnf install -y nasm \
    && dnf clean all \
    && rm -rf /var/cache/dnf
RUN pipx install --force "cmake<4"


# -------------------------------- libheif-deps ----------------------------------------
FROM base AS libheif-deps

ENV X265_VERSION=4.1
RUN set -ex \
    && curl -fLO https://bitbucket.org/multicoreware/x265_git/downloads/x265_${X265_VERSION}.tar.gz \
    && tar xvf x265_${X265_VERSION}.tar.gz \
    && cd x265_${X265_VERSION} \
    && cmake -DCMAKE_INSTALL_PREFIX=/usr -G "Unix Makefiles" ./source \
    && make -j $(nproc) && make install && ldconfig \
    && rm -rf /build

ENV LIBDE265_VERSION=1.0.16
RUN set -ex \
    && curl -fLO https://github.com/strukturag/libde265/releases/download/v${LIBDE265_VERSION}/libde265-${LIBDE265_VERSION}.tar.gz \
    && tar xvf libde265-${LIBDE265_VERSION}.tar.gz \
    && cd libde265-${LIBDE265_VERSION} \
    && ./autogen.sh \
    && CXXFLAGS="-g1 -O2" ./configure --prefix /usr --disable-encoder --disable-dec265 \
        --disable-sherlock265 --disable-dependency-tracking \
    && make -j $(nproc) && make install && ldconfig \
    && rm -rf /build

ENV LIBAOM_VERSION=v3.13.1
RUN set -ex \
    && mkdir -v aom && mkdir -v aom_build && cd aom \
    && curl -fLO "https://aomedia.googlesource.com/aom/+archive/${LIBAOM_VERSION}.tar.gz" \
    && tar xvf ${LIBAOM_VERSION}.tar.gz \
    && cd ../aom_build \
    && MINIMAL_INSTALL="-DENABLE_TESTS=0 -DENABLE_TOOLS=0 -DENABLE_EXAMPLES=0 -DENABLE_DOCS=0" \
    && cmake $MINIMAL_INSTALL -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_INSTALL_LIBDIR=lib -DBUILD_SHARED_LIBS=1 ../aom \
    && make -j $(nproc) && make install && ldconfig \
    && rm -rf /build


# -------------------------------- libheif ---------------------------------------------
FROM libheif-deps AS libheif
ARG LIBHEIF_VERSION

RUN set -ex \
    && LIBHEIF_VERSION="$LIBHEIF_VERSION" \
    && curl -fLO https://github.com/strukturag/libheif/releases/download/v${LIBHEIF_VERSION}/libheif-${LIBHEIF_VERSION}.tar.gz \
    && tar xvf libheif-${LIBHEIF_VERSION}.tar.gz && mv libheif-${LIBHEIF_VERSION} libheif \
    && mkdir libheif_build && cd libheif_build \
    && cmake --install-prefix=/usr --preset=release-noplugins -DWITH_EXAMPLES=no ../libheif \
    && make -j $(nproc) && make install && ldconfig \
    && rm -rf /build


# -------------------------------- wheel -----------------------------------------------
FROM libheif AS wheel
ARG PYTHON_VERSION

COPY ./ /pyheif

RUN set -ex \
    && /opt/python/${PYTHON_VERSION}/bin/pip wheel /pyheif \
    && auditwheel repair pyheif*.whl -w /wheels


# -------------------------------- tested ----------------------------------------------
FROM base AS tested
ARG PYTHON_VERSION

COPY ./requirements-test.txt /tmp/requirements-test.txt

RUN /opt/python/${PYTHON_VERSION}/bin/pip install --only-binary :all: -r /tmp/requirements-test.txt

COPY --from=wheel /wheels /wheels
COPY ./ /pyheif
WORKDIR /pyheif

RUN set -ex \
    && PNV="/opt/python/${PYTHON_VERSION}/bin" \
    && $PNV/pip install /wheels/pyheif-*.whl \
    && $PNV/pytest
