FROM quay.io/pypa/manylinux2014_x86_64 AS base

###############
# Build tools #
###############

FROM base AS build-tools

# pkg-config
RUN set -ex \
    && mkdir -p /build-tools && cd /build-tools \
    && PKG_CONFIG_VERSION="0.29.2" \
    && curl -fLO https://pkg-config.freedesktop.org/releases/pkg-config-${PKG_CONFIG_VERSION}.tar.gz \
    && tar xvf pkg-config-${PKG_CONFIG_VERSION}.tar.gz \
    && cd pkg-config-${PKG_CONFIG_VERSION} \
    && ./configure \
    && make -j4 \
    && make install \
    && pkg-config --version \
    && rm -rf /build-tools

# nasm
RUN set -ex \
    && mkdir -p /build-tools && cd /build-tools \
    && NASM_VERSION="2.15.02" \
    && curl -fLO https://www.nasm.us/pub/nasm/releasebuilds/${NASM_VERSION}/nasm-${NASM_VERSION}.tar.gz \
    && tar xvf nasm-${NASM_VERSION}.tar.gz \
    && cd nasm-${NASM_VERSION} \
    && ./configure \
    && make -j4 \
    && make install \
    && nasm --version \
    && rm -rf /build-tools

################
# Dependencies #
################

FROM build-tools AS build-deps

# x265
RUN set -ex \
    && mkdir -p /build-deps && cd /build-deps \
    && X265_VERSION="3.5" \
    && curl -fLO https://bitbucket.org/multicoreware/x265_git/downloads/x265_${X265_VERSION}.tar.gz \
    && tar xvf x265_${X265_VERSION}.tar.gz \
    && cd x265_${X265_VERSION} \
    && cmake -DCMAKE_INSTALL_PREFIX=/usr -G "Unix Makefiles" ./source \
    && make -j4 \
    && make install \
    && ldconfig \
    && rm -rf /build-deps

# libde265
RUN set -ex \
    && mkdir -p /build-deps && cd /build-deps \
    && LIBDE265_VERSION="1.0.8" \
    && curl -fLO https://github.com/strukturag/libde265/releases/download/v${LIBDE265_VERSION}/libde265-${LIBDE265_VERSION}.tar.gz \
    && tar xvf libde265-${LIBDE265_VERSION}.tar.gz \
    && cd libde265-${LIBDE265_VERSION} \
    && ./autogen.sh \
    && ./configure --prefix /usr --disable-encoder --disable-dec265 --disable-sherlock265 --disable-dependency-tracking \
    && make -j4 \
    && make install \
    && ldconfig \
    && rm -rf /build-deps

# libaom
RUN set -ex \
    && mkdir -p /build-deps && cd /build-deps \
    && LIBAOM_VERSION="v3.2.0" \
    && mkdir -v aom && mkdir -v aom_build && cd aom \
    && curl -fLO "https://aomedia.googlesource.com/aom/+archive/${LIBAOM_VERSION}.tar.gz" \
    && tar xvf ${LIBAOM_VERSION}.tar.gz \
    && cd ../aom_build \
    && MINIMAL_INSTALL="-DENABLE_TESTS=0 -DENABLE_TOOLS=0 -DENABLE_EXAMPLES=0 -DENABLE_DOCS=0" \
    && cmake $MINIMAL_INSTALL -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_INSTALL_LIBDIR=lib -DBUILD_SHARED_LIBS=1 ../aom \
    && make -j4 \
    && make install \
    && ldconfig \
    && rm -rf /build-deps

# libheif
RUN set -ex \
    && mkdir -p /build-deps && cd /build-deps \
    && LIBHEIF_VERSION="1.12.0" \
    && curl -fLO https://github.com/strukturag/libheif/releases/download/v${LIBHEIF_VERSION}/libheif-${LIBHEIF_VERSION}.tar.gz \
    && tar xvf libheif-${LIBHEIF_VERSION}.tar.gz \
    && cd libheif-${LIBHEIF_VERSION} \
    && ./configure --prefix /usr --disable-examples \
    && make -j4 \
    && make install \
    && ldconfig \
    && rm -rf /build-deps

##########################
# Build manylinux wheels #
##########################

FROM build-deps AS repaired

COPY ./ /pyheif

# python 3.6
RUN set -ex \
    && cd "/opt/python/cp36-cp36m/bin/" \
    && ./pip wheel /pyheif \
    && auditwheel repair pyheif*.whl --plat manylinux2014_x86_64 -w /wheelhouse
# python 3.7
RUN set -ex \
    && cd "/opt/python/cp37-cp37m/bin/" \
    && ./pip wheel /pyheif \
    && auditwheel repair pyheif*.whl --plat manylinux2014_x86_64 -w /wheelhouse
# python 3.8
RUN set -ex \
    && cd "/opt/python/cp38-cp38/bin/" \
    && ./pip wheel /pyheif \
    && auditwheel repair pyheif*.whl --plat manylinux2014_x86_64 -w /wheelhouse
# python 3.9
RUN set -ex \
    && cd "/opt/python/cp39-cp39/bin/" \
    && ./pip wheel /pyheif \
    && auditwheel repair pyheif*.whl --plat manylinux2014_x86_64 -w /wheelhouse
# python 3.10
RUN set -ex \
    && cd "/opt/python/cp310-cp310/bin/" \
    && ./pip wheel /pyheif \
    && auditwheel repair pyheif*.whl --plat manylinux2014_x86_64 -w /wheelhouse
# pypy 3.7
RUN set -ex \
    && cd "/opt/python/pp37-pypy37_pp73/bin/" \
    && ./pip wheel /pyheif \
    && auditwheel repair pyheif*.whl --plat manylinux2014_x86_64 -w /wheelhouse
# pypy 3.8
RUN set -ex \
    && cd "/opt/python/pp38-pypy38_pp73/bin/" \
    && ./pip wheel /pyheif \
    && auditwheel repair pyheif*.whl --plat manylinux2014_x86_64 -w /wheelhouse


###############
# Test wheels #
###############

FROM base AS tested

COPY --from=repaired /wheelhouse /wheelhouse
COPY ./ /pyheif
WORKDIR /pyheif

# python 3.6
RUN set -ex \
    && PNV="/opt/python/cp36-cp36m/bin" \
    && $PNV/pip install -r /pyheif/requirements-test.txt /wheelhouse/*-cp36-cp36m-*.whl \
    && $PNV/pytest
# python 3.7
RUN set -ex \
    && PNV="/opt/python/cp37-cp37m/bin" \
    && $PNV/pip install -r /pyheif/requirements-test.txt /wheelhouse/*-cp37-cp37m-*.whl \
    && $PNV/pytest
# python 3.8
RUN set -ex \
    && PNV="/opt/python/cp38-cp38/bin" \
    && $PNV/pip install -r /pyheif/requirements-test.txt /wheelhouse/*-cp38-cp38-*.whl \
    && $PNV/pytest
# python 3.9
RUN set -ex \
    && PNV="/opt/python/cp39-cp39/bin" \
    && $PNV/pip install -r /pyheif/requirements-test.txt /wheelhouse/*-cp39-cp39-*.whl \
    && $PNV/pytest
# python 3.10
RUN set -ex \
    && PNV="/opt/python/cp310-cp310/bin" \
    && $PNV/pip install -r /pyheif/requirements-test.txt /wheelhouse/*-cp310-cp310-*.whl \
    && $PNV/pytest
# pypy 3.7
RUN set -ex \
    && PNV="/opt/python/pp37-pypy37_pp73/bin/" \
    && $PNV/pip install -r /pyheif/requirements-test.txt /wheelhouse/*-pp37-pypy37_pp73-*.whl \
    && $PNV/pytest
# No Pillow wheels for pypy 3.8
# # pypy 3.8
# RUN set -ex \
#     && PNV="/opt/python/pp38-pypy38_pp73/bin/" \
#     && $PNV/pip install -r /pyheif/requirements-test.txt /wheelhouse/*-pp38-pypy38_pp73-*.whl \
#     && $PNV/pytest

#################
# Upload wheels #
#################

FROM tested AS uploaded

ARG PYPI_USERNAME
ARG PYPI_PASSWORD
RUN set -ex \
    && cd "/opt/python/cp38-cp38/bin/" \
    && ./pip install twine \
    && ./twine upload /repaired/*manylinux2014*.whl -u ${PYPI_USERNAME} -p ${PYPI_PASSWORD} \
