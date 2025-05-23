#!/bin/bash

# Log work entries
./aldo_cli.py log 2025-04-01 1
./aldo_cli.py log 2025-04-02 1 
./aldo_cli.py log 2025-04-03 1
./aldo_cli.py generate-invoice 2025-04-03 -o simple_test.pdf
./aldo_cli.py confirm 10
./aldo_cli.py log 2025-04-04 1
./aldo_cli.py log 2025-04-05 2
./aldo_cli.py log 2025-04-06 3
./aldo_cli.py log 2025-04-07 4
./aldo_cli.py generate-invoice 2025-04-05 -o complex_test.pdf
./aldo_cli.py confirm 20
