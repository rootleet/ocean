#!/bin/bash
curl --location --request PUT 'http://127.0.0.1/retail/api/' \
--header 'Content-Type: application/json' \
--header 'Cookie: csrftoken=etMJ2XQLTdShoVg4UxIfhE67JjVuYtNP' \
--data '{
    "module":"sync_retail_groups",
    "data":{}
}'