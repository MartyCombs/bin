#!/usr/bin/env bash

PrintUsage() {
    cat <<EOF
    $(basename $0) [ -e EMAIL ]

Performs a whois query 
EOF
}

while getopts "e:" optchar; do
    case "${optchar}" in 
        "e") EMAIL="${OPTARG}" ;;
    esac
done
shift $((OPTIND-1))
if [ ${#} -lt 0 ]; then
