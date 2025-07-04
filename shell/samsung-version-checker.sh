#! /bin/bash

MODEL="$1"
REGION="$2"

if [[ -z "$MODEL" || -z "$REGION" ]]; then
    echo "No model or region set"
    exit 1
fi

get_model_id() {
    echo $(curl -SsL "https://doc.samsungmobile.com/$MODEL/$REGION/doc.html" | grep English | cut -d"/" -f 4)
}

get_latest_android_version() {
    local model_id="$1"
    if [[ -z "$model_id" ]]; then
        echo "No model id found"
        exit 1
    fi
    echo $(curl -SsL "https://doc.samsungmobile.com/$MODEL/$model_id/eng.html?timestamp=Wed%20May%2021%202025%2008:58:43%20GMT-0300%20(Brasilia%20Standard%20Time)" | grep "Android version" | head -n 1 | cut -d"(" -f 2 | cut -d")" -f 1)
}


while true; do
MODEL_ID=$(get_model_id)
LATEST=$(get_latest_android_version $MODEL_ID)
echo "$LATEST" | grep 15
if [[ "$?" == "0" ]]; then
    notify-send "Update Watcher" "New Android 15 released for A55" -t 5000
    echo -n $(date)
    echo ": Update found"
    exit 0
else
    echo "No updates"
fi
sleep 60
done
