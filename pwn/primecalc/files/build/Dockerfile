FROM python:3.13-slim AS dmtcp-builder
RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates curl gcc g++ make \
 && rm -rf /var/lib/apt/lists/*
ARG DMTCP_VERSION=4.2.0
RUN curl -fsSL "https://github.com/dmtcp/dmtcp/archive/refs/tags/v${DMTCP_VERSION}.tar.gz" \
      -o /tmp/dmtcp.tar.gz \
 && mkdir /tmp/dmtcp-src \
 && tar -xzf /tmp/dmtcp.tar.gz -C /tmp/dmtcp-src --strip-components=1 \
 && cd /tmp/dmtcp-src \
 && ./configure --prefix=/opt/dmtcp \
 && make -j"$(nproc)" \
 && make install

FROM python:3.13-slim
RUN apt-get update \
 && apt-get install -y --no-install-recommends gzip libatomic1 libstdc++6 tini gcc libc6-dev \
 && rm -rf /var/lib/apt/lists/*
COPY --from=dmtcp-builder /opt/dmtcp /opt/dmtcp
ENV PATH=/opt/dmtcp/bin:$PATH DATA_DIR=/app/data
WORKDIR /app
COPY payload.c /payload.c
RUN gcc -O0 -static-libgcc -o /payload /payload.c
COPY make_ckpt.sh /make_ckpt.sh
RUN sed -i 's/\r$//' /make_ckpt.sh && chmod +x /make_ckpt.sh
CMD ["sh","/make_ckpt.sh"]
