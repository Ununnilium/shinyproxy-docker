NAME  := shinyproxy
IMAGE := $(NAME)

all: build_img

.PHONY: build_img run

build_img:
	docker pull `sed -n 's/^FROM \(.*\)$$/\1/p' Dockerfile`
	docker build -t $(IMAGE):latest --force-rm=true --squash . || \
		docker build -t $(IMAGE):latest --force-rm=true .

run:
	@port="`sed -n 's!\s*port:\s*\(.*\)$$!\1!p' application.yml`" && \
	context_path="`sed -n 's!\s*contextPath:\s*\(.*\)$$!\1!p' application.yml`" && \
	printf "\n\033[;32mShiny Proxy will be available at http://127.0.0.1:$$port$$context_path\033[0m\n\n" && \
	docker run --net=iw_net --name shinyproxy -p 127.0.0.1:$$port:$$port -v /var/run/docker.sock:/var/run/docker.sock $(IMAGE)
