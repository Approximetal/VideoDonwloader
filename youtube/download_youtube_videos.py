import langid
import os, time
import argparse
# import youtube_dl
import yt_dlp as youtube_dl
from tqdm import tqdm
from functools import partial
from concurrent.futures import ProcessPoolExecutor


class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

def duration_filter(info, dur=3600):
    """Download only videos longer than an hour (or with unknown duration)"""
    duration = info.get('duration')
    if duration and duration < dur:
        return False
    else:
        return True

def download(youtube_url, save_dir, lang):
    save_path = os.path.join(save_dir, "%(uploader)s_%(title).20s_%(id)s.%(ext)s") # 
    ydl_opts = {
        # outtmpl 格式化下载后的文件名，避免默认文件名太长无法保存
        'outtmpl': save_path,
        'logger': MyLogger(),
        'ignoreerrors': True,
        'writeinfojson': True,
        'writesubtitles': True,
        'allsubtitles': True,
        'subtitleslangs':[lang],
        # 'match_filter': duration_filter,
        # 'merge_output_format':'webm',
        # 'playliststart': last_dl_index + 1,
        # 'playlistend': end_dl_index,        # stop downloading at this index
        # 'user-agent':"your bot 0.1"
        # 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    }
    ydl = youtube_dl.YoutubeDL(ydl_opts)
    with ydl:
        try:
            res = ydl.extract_info(youtube_url, download=False)
            print(res['title'], res['duration'], '\n')
            if langid.classify(res['title'])[0] != lang:
                return
            # if res['duration'] < 3600:
            #     return
            ydl.download([youtube_url])
            print(res['title'], 'OK')
            time.sleep(0.5)
        except Exception as e:
            print(e)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--lang', type=str, default='en', help='See ISO 639-1 codes for supported languages (total: 97).')
    parser.add_argument('--list_dir', type=str, default='./list', help='Dictionary path of saved channel lists.')
    parser.add_argument('--save_dir', type=str, default='./download', help='Dictionary path to save youtube videos.')
    parser.add_argument('--workers', type=int, default=8, help='Multiprocess workers.')
    args = parser.parse_args()

    if not os.path.exists(args.save_dir):
        os.makedirs(args.save_dir, exist_ok=True)
        exist_files = set()
    
    # Start multiprocess
    executor = ProcessPoolExecutor(max_workers=args.workers)
    print(f"> Using {args.workers} workers!")
  
    
    for root, _, files in os.walk(args.list_dir):
        futures = []
        exist_files = os.listdir(args.save_dir)
        exist_files = set([x.split('.')[-2][-11:] for x in exist_files if x[-4:] in {'.mov', '.avi', '.flv', '.ogg', '.mp4', '.mkv', 'webm'}])
        print('已下载视频：', len(exist_files))
        for f in files:
            list_file = os.path.join(root, f)
            if not list_file.endswith('.txt'):
                continue

            with open(list_file, 'r', encoding='utf-8') as load_f:
                for line in tqdm(load_f.readlines()):
                    line = str(line).strip().split('|')
                    if len(line)<2:
                        continue
                    if line[1] in exist_files:
                        continue
                    link = "https://www.youtube.com/watch?v=" + line[1]
                    # print(link, '|'.join(line))
                    # download(link, args.save_dir, args.lang)
                    futures.append(executor.submit(partial(download, link, args.save_dir, args.lang)))


        result_list = [future.result() for future in tqdm(futures)]
        print(len(result_list), 'videos downloaded.')

if __name__ == '__main__':
    main()
