## 1. 安装依赖包


- 安装 [youtube-dlp](https://github.com/yt-dlp/yt-dlp)) 

    ```pip install git+https://github.com/yt-dlp/yt-dlp.git```


## 2. 下载YouTube视频

- 根据关键词下载YouTube视频

    1) 首先确定语言和关键词，爬取所有符合条件的youtube链接，并进行去重
    2) 根据列表进行多进程下载，可设置参数过滤下载条件

    ```
    python crawl_youtube_links.py --lang en --keywords Trump,Obama --save_dir ./list
    python download_youtube_videos.py --lang en --list_dir ./list --save_dir ./download
    ```

- 根据频道下载YouTube视频

    1) 首先利用关键词人工筛选频道信息，保存在比如lang_channels.txt文件中，格式为"channel_name\t@channel_name"
    2) 配置下载选项，比如最佳音质、视频分辨率、设置视频或者字幕的过滤条件, 具体参考[此处](https://github.com/yt-dlp/yt-dlp#general-options)
    3) 设置下载文件输出目录，下载的日志信息保存在当前目录log_out中，*.log是过程日志文件，video_*.txt是video_id文件

    ```
    ./download_from_youtube_channels.sh zh_channels_example.txt ./download
    ```
