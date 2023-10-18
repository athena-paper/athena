#!/usr/bin/env bash
# linking example

OUT_DIR=results
CUR_DIR=$(pwd)

automation()
{
    rm -f config.json
    mkdir -p $OUT_DIR
    for f in ./configs/* ; do 
        PROTOCOL=$(echo $f | sed -e 's/.\/configs\/\(.*\).json/\1/')
        echo "Running on [$PROTOCOL]..."

        cp $f ./config.json

        ./run.sh $PROTOCOL
    done
    rm -f config.json
}

main()
{   
    cd $CUR_DIR
    echo "Running all protocol evaluation..."
    echo "----------------------------------"
    automation
}

main