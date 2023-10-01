#!/usr/bin/env bash

curl --location --request VIEW 'http://127.0.0.1/adapi/' \
--header 'Content-Type: application/json' \
--header 'Cookie: csrftoken=etMJ2XQLTdShoVg4UxIfhE67JjVuYtNP' \
--data '{
    "module":"dept_report"
}'