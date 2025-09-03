dc := "docker compose"
dcservice_web := "web"
dcservice_db := "db"
dcservice_test := "test"
dcservice_default := dcservice_web
dcrun := dc + " run --rm"
dcexec := dc + " exec"
dcrun_bg := dc + " run --rm -d"
iex := dcrun + " " + dcservice_web + " iex"
default_remote_env := "qa"
app_name := "boruta_example_official"

set dotenv-load
set dotenv-path := ".env"

default: up

build:
    {{dc}} build #--no-cache

down:
	{{dc}} down -v --remove-orphans

up service=dcservice_default bg="":
    {{dc}} up {{ if bg == "bg" { "-d" } else { "" } }} {{service}}

test bg="":
    {{dc}} up {{ if bg == "bg" { "-d" } else { "" } }} {{dcservice_test}}

bash service=dcservice_default:
    {{dcrun}} {{service}} bash

psql service=dcservice_default:
	{{dcrun}} {{service}} psql

db-dump env=default_remote_env jobs="10":
    pg_dump -v -h localhost -p ${AWS_JUMPBOX_TUNNEL_LOCAL_PORT} -U postgres -d {{env}}_validate_ai_backend -Fd -j {{jobs}} -f db_dumps/{{env}}_validate_ai_backend_$(date +"%Y%m%d_%H%M%S")


#db-restore-dev input="" jobs="10": down
#    sh devops/recreate_local_db.sh
#    pg_restore --no-acl --no-owner -v -h localhost -p 5432 -U postgres -j {{jobs}} -Fd -d dev_validate_ai_backend {{input}}
#    {{alembic}} upgrade head
#    {{dcrun}} -p 45484:45484 -d {{dcservice_web}} blackd --bind-host 0.0.0.0

iex OPTIONS:
    {{iex}} {{OPTIONS}}

