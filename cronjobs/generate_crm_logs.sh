#!/bin/bash
curl --location --request VIEW 'http://127.0.0.1/crm/api/' \
--header 'Content-Type: application/json' \
--header 'Cookie: csrftoken=etMJ2XQLTdShoVg4UxIfhE67JjVuYtNP' \
--data '{
  "module": "generate_log_report"
}'