#!/bin/sh

base=${1}
schema=${base}/schema.json
input_data=${base}/data.json.gz
output_data=${base}/output*json.gz
data=${input_data} && [[ -e ${output_data} ]] && data=${output_data}
model=${base}/model*pkl.gz
model_structure=${base}/structure*json

if [ -e ${schema} ]
then
    python manage.py cih create_project --schema_file ${schema}
    python manage.py makemigrations interact
    python manage.py migrate interact
    #if [ -e ${model} ]
    #then
    # 	python manage.py cih place_model --schema_file ${schema} --model_file ${model}
    # fi
    if [ -e ${data} ]
    then
	python manage.py cih upload_data --schema_file ${schema} --data_file ${data}	
	for tp in structure topic tsne liwc structure
	do
	    item=${base}/${tp}*z
	    if [ -e ${item} ]
	    then
		python manage.py cih upload_${tp} --schema_file ${schema} --${tp}_file ${item}
	    fi
	done
    fi
fi

