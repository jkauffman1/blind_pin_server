## What is this repo?

This repo contains the oracle server that helps enforce 3 PIN tentatives on [Jade](https://github.com/Blockstream/Jade).

The oracle is blind to the pin and should be easy to run an instance of the
server over Tor.

In the future we plan to use the pin server in other projects such as Blockstream
Green.

## Build the docker image

`docker build -t pinserver .`

## Prepare the directory for all the pins (optional, if you want to persist pins)

`mkdir pinsdir`

## Run the docker image (requires the previous steps)

To persist the pin data mount a volume into the `/pins` directory.

To persist the server private key mount a file at `/server_private_key.key`.

`docker run -v $PWD/server_private_key.key:/server_private_key.key -v $PWD/pinsdir:/pins -p 8096:8096 dockerized_pinserver`

If you run the container without mounting any files/volumes it will create ephemeral server keys
and pins, which is useful in development environments.

`docker run -p 8096:8096 pinserver`

You can verify the server is working on port 8096 like this:

`curl -X POST localhost:8096/start_handshake`

## Devlopment/debugging

It can be useful to bind mount your local filesystem

`docker run -v ${PWD}:/pinserver/ -p 8096:8096 pinserver`
