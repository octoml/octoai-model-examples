## CLIP Interrogator Model Endpoint

This CLIP Interrogator model relies on the following python library: https://github.com/pharmapsychotic/clip-interrogator

CLIP interrogator performs image to text labeling. The Interrogator model we're using is based on OpenAI's ViT-L-14.

## Pre-requisites

You'll need docker installed on the machine you'll run the steps below. You can install docker engine from the following link: https://docs.docker.com/engine/install/

Check that docker has been installed by typing `docker` in your terminal.

Next, install the OctoAI CLI from the Installation documentation webpage: https://docs.octoai.cloud/docs/installation-links.

Then test that you're using the right octoai CLI version (0.5.13 or newer) with `octoai version`:
```
▓▓▓ octoai

  Version            0.5.13
  Git Commit         67d6272
  Build Date         12 Jan 24 15:11 EST (4 days ago)
  Commit Date        12 Jan 24 15:11 EST (4 days ago)
  Dirty Build        no
  Go version         1.21.5
  Compiler           gc
  Platform           darwin/arm64
```

For more information on how to build a model container with the CLI, check out: https://docs.octoai.cloud/docs/containerize-your-code-with-our-cli

## Build a model container

Let's build and test the CLIP-Interrogator model based on SD1.5.

```
octoai init --path .
```

Follow the prompts to configure your endpoint:
* Name your endpoint (e.g. clip-interrogator)
* Select an endpoint, you'll require an `gpu.a10g.medium` or better
* No need to set new secrets, so select `(None/No More)`
* No need to add environment variables, so select `(None/No More)`

Once you're done, you'll get an output as follows:
```text
Initialized project in <projectpath>/octoai-model-examples/image2text/clip-interrogator-sd15. Build your endpoint with:

	cd /Users/moreau/Documents/Projects/octoai-model-examples/image2text/clip-interrogator-sd15
	octoai build

You can configure your project by editing the octoai.yaml file.

For the OctoAI CLI developer documentation, please visit https://docs.octoai.cloud/docs/containerize-your-code-with-our-cli
```

You can always edit your model endpoint settings by editing the automatically generated `octoai.yaml` file
```
endpoint_config:
  name: clip-interrogator
  hardware: gpu.a10g.medium
  registry:
    host: r.octoai.cloud
    # warning: registry path must begin with account key <ACCOUNTKEY> when using OctoAI Image Registry
    path:  <ACCOUNTKEY>/clip-interrogator
version_info:
  cli_version: 0.5.13
  sdk_version: 0.8.2
```

We're ready to fire off the build now. There are two methods depending on whether you want to modify the Dockerfile that is used to build our model container.

1. If you don't want to change the Dockerfile that is used to generate the model container, you can just run
```bash
octoai build
```

2. If you do want to change the Docker file that is used to generate the model container (e.g. you want to change the software dependencies), you can run:
```bash
octoai build -g
# This will create a Dockerfile in your project directory
# Inspect and modify the Dockerfile as needed
octoai build
# The command above will build the model container using the Dockerfile
# in your project directory instead of the pre-defined one
```

See the standard Dockerfile that gets used by default
```dockerfile
FROM octoml/base-torch:2.0.1-cuda-12.0
ENV DEBIAN_FRONTEND="noninteractive"
ENV PYTHONUNBUFFERED=1
RUN apt update && apt install -y \
  ffmpeg \
  libsm6 \
  libxext6 \
  libgl1 \
  python3-pip \
  && rm -rf /var/lib/apt/lists/* \
  && pip install --no-cache-dir --upgrade pip

# Ensure CUDART libraries can be found are on the library path.
ARG CUDART_PATH=/usr/local/cuda/lib64
ENV LD_LIBRARY_PATH=${CUDART_PATH}:${LD_LIBRARY_PATH}
RUN ln -s ${CUDART_PATH}/libcudart.so.12 ${CUDART_PATH}/libcudart.so
RUN ln -s ${CUDART_PATH}/libnvrtc.so.12 ${CUDART_PATH}/libnvrtc.so
RUN ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /service

# Install server wheel.

RUN python3 -m pip install octoai-sdk==0.8.2


# Install template dependencies.
COPY app/requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# Copy remaining template contents.
COPY app .

ENTRYPOINT ["python3", "-m", "octoai.server", "--service-module", "service", "run"]
```

## Test the model locally (GPU machines only)

Each model includes a `test_request.py`` file which has a example request for its corresponding model. By default it is configured to send the requests to the model container running locally.

Run the following command to test the container if your development machine is equipped with a powerful enough Nvidia GPU. If you don't have access to one, no problem just go to the next step.

```bash
octoai run --gpus all -l --command "python3 test_request.py"
```

## Deploy on OctoAI endpoint

Deploy on an OctoAI endpoint with the following command:

```bash
octoai deploy
```

This will take some time for the container image uploaded to OctoAI's registry depending on your network speed (the container image is several GBs large).

Once the endpoint is up and running, you'll get the following confirmation message from the CLI.

```
Your endpoint "clip-interrogator" has been successfully deployed at <CLIP-ENDPOINT-URL>.

To get information on your endpoint:

	octoai endpoint get --name clip-interrogator
```

Note the endpoint URL since this is the URL we'll use to test our endpoint.

## Test the model remotely

To test the endpoint remotely run the following command:

```bash
python3 test_request.py --endpoint=<CLIP-ENDPOINT-URL>
```

The model endpoint will likely need to go through a cold start the first time you hit it so the first test could take some time (in the order of several minutes). This is because the OctoAI endpoint needs to first pull and cache the container image you just uploaded to the docker image registry. Then it needs to start the container and download the model weights. Subsequent calls to your model endpoint will lead to much shorter times.

This should produce the following output:
```text
CLIP interrogator description from SD1.5: a blue whale with a container on its back and a building in the back, subreddit / r / whale, blue whale, corporate phone app icon, app icon, icon for an ai app, inspired by Karl Ballmer, whale, 🐋 as 🐘 as 🤖 as 👽 as 🐳, by Karl Ballmer, single logo, best logo
```

By default your endpoint should automatically scale down (assuming you've left min replicas to 0). You can always manage your compute endpoints on OctoAI's website using the Compute Solution UI under https://octoai.cloud/endpoints.