.PHONY: check_libheif_versions

PLAT ?= manylinux2014_x86_64

check_libheif_versions:
	docker build --target=libheif --build-arg=PLAT=${PLAT} --build-arg=LIBHEIF_VERSION=1.16.2 .
	docker build --target=libheif --build-arg=PLAT=${PLAT} --build-arg=LIBHEIF_VERSION=1.17.0 .
	docker build --target=libheif --build-arg=PLAT=${PLAT} --build-arg=LIBHEIF_VERSION=1.17.5 .
	docker build --target=libheif --build-arg=PLAT=${PLAT} --build-arg=LIBHEIF_VERSION=1.17.6 .
	docker build --target=libheif --build-arg=PLAT=${PLAT} --build-arg=LIBHEIF_VERSION=1.18.0 .
	docker build --target=libheif --build-arg=PLAT=${PLAT} --build-arg=LIBHEIF_VERSION=1.18.1 .
	docker build --target=libheif --build-arg=PLAT=${PLAT} --build-arg=LIBHEIF_VERSION=1.18.2 .

test:
	docker build --target=tested --build-arg=PLAT=${PLAT} .
