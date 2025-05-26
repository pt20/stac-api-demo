#!/usr/bin/env bash

set -o verbose
set -o errexit

pip install pypgstac[psycopg]
pypgstac migrate
