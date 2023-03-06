:: This file is incomplete, needs better path logging, structuring and other
:: cosmetic work. Writing these commands so that I do not forget them.
:: DO NOT RUN THIS BATCH FILE AS IS. IT IS NOT READY.

:: Create a docker network on the host machine so that two or containers can
:: communicate with each other.
docker network create pxnet

:: Build the docker image
docker build --tag pxsim_img .

:: Run the docker container
docker run --name pxsim --network=pxnet --detach -p 11204:11204 pxsim_img