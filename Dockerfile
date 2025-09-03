FROM elixir:1.14

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
 && apt-get install -y apt-utils \
 && apt-get install -y build-essential \
 && apt-get install -y inotify-tools \
 && apt-get install -y postgresql-client

RUN apt-get install -y libcurl4-openssl-dev libssl-dev libevent-dev

RUN mkdir /boruta_example
WORKDIR /boruta_example

COPY . /boruta_example

RUN mix local.hex --force
RUN mix local.rebar --force

#RUN mix archive.install --force hex phx_new 1.7.2 -> doesn't work https://elixirforum.com/t/creating-a-new-phoenix-project-on-windows-fails-on-extracting-pento-assets-vendor-heroicons-optimized/68143
#RUN mix archive.install --force hex phx_new
#RUN mix do deps.get, deps.compile, compile

RUN mix do clean, deps.get
RUN mix compile

CMD ["/boruta_example/entrypoint.sh"]
