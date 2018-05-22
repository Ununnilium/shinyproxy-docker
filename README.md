# Shiny Proxy in a Docker Container #

This repository contains the code and configuration to run [ShinyProxy](https://github.com/openanalytics/shinyproxy)
(more info at [shinyproxy.io](https://www.shinyproxy.io)) inside a Docker container.

## Usage ##
1. Configure ShinyProxy in `application.yml` and modify the configuration block in `shiny_start.py`
2. Build the image with `make`
3. Run the Shiny Proxy container with `make run`
