# docker-hosted-znc

PonyChat uses [ZNC](http://znc.in) for its bouncer. This is how we do it.

## Usage

```console
$ docker build -t ponychat/znc .
$ docker volume create --name bnc-data
$ docker run --rm -itv bnc-data:/home/bnc/.znc alpine:3.4 sh -c 'chmod a+rwx /home/bnc/.znc'
$ docker run \
    -e ATHEME_SERVER="ip:port" \
    -e IRC_NETWORK_NAME="FooNet" \
    -e IRC_NETWORK_DOMAIN="foo.net" \
    -p 6697:6697 -v bnc-data:/home/bnc/.znc \
    ponychat/znc
```
