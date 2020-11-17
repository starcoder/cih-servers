#!/bin/sh
base=$1
scripts/reset_db.sh
for x in ${1}/work/*/schema.json
do
    base=`dirname ${x}`
    project=`basename ${base}`
    if [[ "${project}" != "multimodal_wikipedia" ]]
    then
	scripts/add_project.sh ${base}
    fi
done
