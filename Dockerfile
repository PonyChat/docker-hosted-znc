FROM alpine:3.4

EXPOSE 8080
EXPOSE 6697

ENV HOME /home/bnc

RUN apk add --no-cache ca-certificates znc znc-modpython znc-extra \
 && adduser -D bnc

ADD *.py /usr/lib/znc/
ADD ./znc.conf /orig/znc.conf
ADD ./znc.pem /orig/znc.pem
ADD ./run.sh /run.sh

USER bnc

VOLUME /home/bnc/.znc

CMD /run.sh
