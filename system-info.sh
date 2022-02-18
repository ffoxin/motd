#!/usr/bin/env sh

script_dir=$(dirname $0)
"exec" "$script_dir/venv/bin/python" "$script_dir/system-info.py"

