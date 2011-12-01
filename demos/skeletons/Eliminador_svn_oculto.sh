#!/bin/bash

function rec_eliminador {
    echo "Eliminando .svn en "$(pwd)/$1
    cd "$1";
    rm -rf .svn;
    for subdir in $(ls --file-type | grep /)
    do
        rec_eliminador "$subdir"
    done
    cd ..
}
echo "Eliminando directorios .svn ocultos"
rec_eliminador .
