.PHONY: check_libheif_versions

ARCH ?= amd64
LIBHEIF_VERSION ?= 1.21.2
PYTHON_VERSION ?= cp312-cp312
DOCKER_IID_FILE = .docker_build-$(ARCH)-$(LIBHEIF_VERSION)-$(PYTHON_VERSION)
DOCKER_BUILD_EXTRA_ARGS ?=


.PHONY: test
test:
	docker build --platform=linux/$(ARCH) --iidfile $(DOCKER_IID_FILE) $(DOCKER_BUILD_EXTRA_ARGS) . \
		--build-arg=LIBHEIF_VERSION=$(LIBHEIF_VERSION) --build-arg=PYTHON_VERSION=$(PYTHON_VERSION)


.PHONY: copy
copy: test
	CID=$$(docker create --platform linux/$(ARCH) $$(cat $(DOCKER_IID_FILE))) \
	&& docker cp $${CID}:/wheels ./ \
	&& docker rm $${CID}
	rm $(DOCKER_IID_FILE)


.PHONY: test_libheif_versions
test_libheif_versions:
	$(MAKE) test LIBHEIF_VERSION=1.16.2
	$(MAKE) test LIBHEIF_VERSION=1.18.2
	$(MAKE) test LIBHEIF_VERSION=1.19.8
	$(MAKE) test LIBHEIF_VERSION=1.20.2
	$(MAKE) test LIBHEIF_VERSION=1.21.2


.PHONY: test_python_versions
test_python_versions:
	$(MAKE) test PYTHON_VERSION=cp38-cp38
	$(MAKE) test PYTHON_VERSION=cp39-cp39
	$(MAKE) test PYTHON_VERSION=cp310-cp310
	$(MAKE) test PYTHON_VERSION=cp311-cp311
	$(MAKE) test PYTHON_VERSION=cp312-cp312
	$(MAKE) test PYTHON_VERSION=cp313-cp313
	$(MAKE) test PYTHON_VERSION=cp314-cp314
	$(MAKE) test PYTHON_VERSION=pp311-pypy311_pp73


.PHONY: copy_python_versions
copy_python_versions:
	$(MAKE) copy PYTHON_VERSION=cp38-cp38
	$(MAKE) copy PYTHON_VERSION=cp39-cp39
	$(MAKE) copy PYTHON_VERSION=cp310-cp310
	$(MAKE) copy PYTHON_VERSION=cp311-cp311
	$(MAKE) copy PYTHON_VERSION=cp312-cp312
	$(MAKE) copy PYTHON_VERSION=cp313-cp313
	$(MAKE) copy PYTHON_VERSION=cp314-cp314
	$(MAKE) copy PYTHON_VERSION=pp311-pypy311_pp73
