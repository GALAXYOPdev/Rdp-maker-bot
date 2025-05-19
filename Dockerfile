FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    xrdp \
    xfce4 \
    xfce4-goodies \
    tightvncserver \
    sudo \
    dbus-x11 \
    && apt-get clean

# Set XFCE as default session
RUN echo "startxfce4" > /etc/skel/.xsession

# Create user 'user' with password 'user'
RUN useradd -m user && echo "user:user" | chpasswd && adduser user sudo

# Configure XRDP to use the user session
RUN sed -i 's/port=3389/port=3389/' /etc/xrdp/xrdp.ini

EXPOSE 3389

CMD ["/usr/sbin/xrdp", "-nodaemon"]
