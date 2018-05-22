# Shiny Proxy in a Docker Container #

This repository contains the code and configuration to run [Shiny Proxy](https://github.com/openanalytics/shinyproxy)
(more info at [shinyproxy.io](https://www.shinyproxy.io)) in side a Docker container.

## Usage ##
1. Configuration Shiny Proxy in `application.yml` and the configuration block in `shiny_start.py`
2. Build the image with `make`
3. Run the Shiny Proxy container with `make run`
