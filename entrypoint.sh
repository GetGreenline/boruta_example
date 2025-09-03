#!/bin/bash

while ! pg_isready -q -h $PGHOST -p $PGPORT -U $PGUSER
  do
    echo "$(date) - waiting for database to start"
    sleep 2
  done

if [[ $MIX_ENV = "test" ]]; then
  mix ecto.reset
  exec mix test
elif [[ $MIX_ENV = "dev" ]]; then
  if [[ -z `psql -Atqc "\\list $PGDATABASE"` ]]; then
    echo "Database $PGDATABASE does not exist. Creating..."
    mix ecto.setup
    echo "Database $PGDATABASE created."
  fi
  echo "Starting Phoenix server..."
  exec mix phx.server
else
  echo "Invalid MIX_ENV variable"
fi
