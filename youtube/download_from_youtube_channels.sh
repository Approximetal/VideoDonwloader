#!/bin/bash

echo "read channels from file: $1, output to dir: $2"

log_dir=log_out
mkdir $log_dir
while read rows
do
  echo "$rows"
  channel=`echo "$rows" | awk -F"\t" '{print $2}'`
  channel_name=`echo ${channel:1}`
  echo "processing channel: $channel, with name: $channel_name"
  nohup yt-dlp -f 'ba' --download-archive $log_dir/audios_$channel_name.txt \
  --write-subs --write-auto-subs --sub-format vtt --sub-langs zh,zh-Hans*,zh-Hant* \
  https://www.youtube.com/${channel}/videos -o ${2}/$channel_name'/%(title).20s#%(channel_id)s#%(id)s_%(duration)s.%(ext)s' > $log_dir/$channel_name.log 2>&1 &
done < $1
echo "finished."

