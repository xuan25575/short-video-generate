import os
import json
import random
import time
from base64 import b64decode
import cv2

# https://blog.csdn.net/jjw_zyfx/article/details/123085349
# 在导入moviepy之前尝试此操作
os.environ["IMAGEIO_FFMPEG_EXE"] = "/Users/code/py/short-video-generate/ffmpeg/ffmpeg"
# os.environ["IMAGEIO_FFMPEG_EXE"] = "/Users/zcy/Library/Python/3.8/lib/python/site-packages/ffmpeg"


from moviepy.editor import AudioFileClip
from moviepy.editor import VideoFileClip, concatenate_videoclips
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from moviepy.editor import *

# ocr 目录路径
ocr_dir_path = r'/Users/code/py/short-video-generate/BaiduImageSpider/ocr_result/搞笑聊天对话'
# 清理后的ocr结果
clean_ocr_dir_path = r'/Users/code/py/short-video-generate/gen/clean_ocr'
# 生成聊天图片的目录
gen_image_dir_path = r'/Users/code/py/short-video-generate/gen/wechat_images'
# 生成视频的目录
gen_video_dir_path = r'/Users/code/py/short-video-generate/gen/wechat_videos'
gen_video_dir_path2 = r'/Users/code/py/short-video-generate/gen/wechat_videos2'
gen_video_dir_path3 = r'/Users/code/py/short-video-generate/gen/wechat_videos3'
# 提取音频的目录
sound_dir_path = r'/Users/code/py/short-video-generate/gen/video_sounds'


# https://blog.csdn.net/SKY_PLA/article/details/123662640
# https://blog.csdn.net/qq_37508131/article/details/123794345
def get_browser():
    url = 'http://127.0.0.1:5000/'
    root_path = os.path.abspath(os.path.dirname(__file__))
    # chrome_driver_path = os.path.join(root_path, 'chromedriver.exe')
    # https://registry.npmmirror.com/binary.html?path=chromedriver/
    chrome_driver_path = os.path.join(root_path, 'chromedriver')  # for mac
    browser = webdriver.Chrome(executable_path=chrome_driver_path)
    browser.get(url)
    return browser


def create_dirs(dir_paths):
    for dir_path in dir_paths:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)


def get_ocr_json(ocr_path):
    for ocr_file_name in os.listdir(ocr_path):
        if ocr_file_name == '.DS_Store':
            continue
        ocr_file_path = os.path.join(ocr_path, ocr_file_name)

        with open(ocr_file_path, 'r', encoding='utf-8') as f:
            ocr_json = f.read()

        ocr_json = json.loads(ocr_json)
        ocr_data_list = ocr_json.get('data', [])  # data: [[...]]

        if ocr_data_list:
            # 真正的数据 {"confidence":0.9937089085578918,"text":"消息（93）",
            # "text_box_position":[[24,14],[121,14],[121,44],[24,44]]}
            ocr_data_list = ocr_data_list[0]
        last_text_box_first_position = 0
        sentences = []

        for ocr_item in ocr_data_list:
            text_box_position = ocr_item.get('text_box_position', [])
            text = ocr_item.get('text', '')

            if not text:
                continue

            if not text_box_position:
                continue

            text_box_first_position_x = text_box_position[0][0]
            text_box_first_position_y = text_box_position[0][1]

            # 很可能是聊天标题
            if text_box_first_position_y < 30:
                continue

            # y轴距离相差小，同一句话
            if last_text_box_first_position and abs(last_text_box_first_position - text_box_first_position_y) < 50:
                item = sentences[-1]
                item['text'] += text
            else:
                if text_box_first_position_x < 150:
                    sentences.append({
                        'postion': 'left',
                        'text': text
                    })
                else:
                    sentences.append({
                        'postion': 'right',
                        'text': text
                    })

            last_text_box_first_position = text_box_first_position_y

        sentences_str = json.dumps(sentences, ensure_ascii=False, indent=4)
        with open(os.path.join(clean_ocr_dir_path, ocr_file_name), 'w', encoding='UTF-8') as f:
            f.write(sentences_str)


def wait_element_xpath(browser, xpath, wait_time=15):
    try:
        WebDriverWait(browser, wait_time, 1).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
    except Exception as e:
        print(f'[wait_element_css] 等待超时, error: {e}')
        raise


# 生成聊天图片
def gen_wechat_image(browser):
    for ocr_file_name in os.listdir(clean_ocr_dir_path):
        if ocr_file_name == '.DS_Store':
            continue
        ocr_file_path = os.path.join(clean_ocr_dir_path, ocr_file_name)
        with open(ocr_file_path, 'r', encoding='utf-8') as f:
            ocr_json = f.read()
        ocr_json_list = json.loads(ocr_json)
        print(ocr_file_path)
        print(ocr_json)
        ocr_file_gen_image_save_dir_path = os.path.join(gen_image_dir_path, ocr_file_name.split('.')[0])
        if not os.path.exists(ocr_file_gen_image_save_dir_path):
            os.makedirs(ocr_file_gen_image_save_dir_path)

        i = 1
        # 清空对话
        time.sleep(0.2)
        # 需要在Chrome可视窗口中
        # clean_chat_input_button = browser.find_element(by=By.XPATH, value='//*[@id="w2"]/div/div[3]/input[2]')
        # ActionChains(browser).click(clean_chat_input_button).perform()

        # 不可行
        # clear_button_xpath = '//*[@id="w2"]/div/div[3]/input[2]'
        # wait_element_xpath(browser, clear_button_xpath)
        # browser.find_element(by=By.XPATH, value=clear_button_xpath).click()

        browser.execute_script("arguments[0].click();",
                               browser.find_element(by=By.XPATH, value='//*[@id="w2"]/div/div[3]/input[2]'))
        for ocr_item in ocr_json_list:

            postion = ocr_item.get('postion')
            text = ocr_item.get('text')
            if not text:
                continue
            if postion == 'right':
                textarea_xpath = '//*[@id="w2"]/div/div[2]/div[1]/div[2]/p[2]/textarea'
                add_text_button_xpath = '//*[@id="w2"]/div/div[2]/div[1]/div[3]/a'
            else:
                textarea_xpath = '//*[@id="w2"]/div/div[2]/div[2]/div[2]/p[2]/textarea'
                add_text_button_xpath = '//*[@id="w2"]/div/div[2]/div[2]/div[3]/a'
            # 添加聊天文字
            time.sleep(0.2)
            text_element = browser.find_element(by=By.XPATH, value=textarea_xpath)
            text_element.clear()
            text_element.send_keys(text)
            # 点击添加对话
            browser.execute_script("arguments[0].click();",
                                   browser.find_element(by=By.XPATH, value=add_text_button_xpath))
            time.sleep(0.2)
            browser.execute_script("arguments[0].click();",
                                   browser.find_element(by=By.XPATH, value='//*[@id="save"]'))
            time.sleep(1)
            base64_img_str = browser.find_element(by=By.XPATH, value='/html/body/div[2]/img').get_attribute('src')
            img_str = base64_img_str.split(",")[-1]  # 删除前面的 “data:image/jpeg;base64,”
            img_str = img_str.replace("%0A", '\n')  # 将"%0A"替换为换行符
            img_data = b64decode(img_str)  # b64decode 解码
            img_path = os.path.join(ocr_file_gen_image_save_dir_path, str(i) + '.jpeg')
            with open(img_path, 'wb') as f:
                f.write(img_data)
            print('img_path: ', img_path)
            # 点击 返回继续修改
            browser.find_element(by=By.XPATH, value='/html/body/div[2]/div/a').click()
            i += 1
        browser.refresh()


def gen_video_from_image():
    for img_dir in os.listdir(gen_image_dir_path):
        if img_dir == '.DS_Store':
            continue
        video_path = os.path.join(gen_video_dir_path, 'temp_'+f'{img_dir}.avi')
        image_folder = os.path.join(gen_image_dir_path, img_dir)
        images = [img for img in os.listdir(image_folder) if img.endswith(".jpeg")]
        if not images:
            continue
        # 第二个参数，flags是读取标记，用来控制读取文件的类型。
        frame = cv2.imread(os.path.join(image_folder, images[0]))  # 读取一幅图像
        height, width, layers = frame.shape  # 表示图像的大小。如果是彩色图像，则返回包含行数、列数和通道数的数组；如果是二值图像或灰度图像，则返回包含行数和列数的数组
        # 第一个参数是要保存的文件的路径,fourcc 指定编码器,fps 要保存的视频的帧率,frameSize 要保存的文件的画面尺寸,isColor 指示是黑白画面还是彩色的画面
        # video = cv2.VideoWriter(video_path, 0, 1, (width, height))
        video = cv2.VideoWriter(video_path, cv2.VideoWriter_fourcc(*'MJPG'), 25, (width, height))
        frame_num = 25 * 10  # 要保存的视频的帧率  * 时间
        length = len(images) # 数组是无序的
        images.sort()
        i = 0
        for index in range(frame_num):
            frame_num_i = cv2.imread(os.path.join(image_folder, images[i]))
            video.write(frame_num_i)
            if index != 0 and index % 25 == 0:
                i += 1
                print(i)
                if i >= length:
                    i = length-1

        # for image in images:
        # video.write(cv2.imread(os.path.join(image_folder, image)))

        cv2.destroyAllWindows()
        video.release()
        print(f'{video_path} 生成成功！')


def get_sound_from_video():
    video_has_sound_path = r'/Users/code/py/short-video-generate/gen/vedio'
    for video_name in os.listdir(video_has_sound_path):
        if video_name == '.DS_Store':
            continue
        sound_name = video_name.split('.')[0]
        video_path = os.path.join(video_has_sound_path, video_name)
        audio_clip = AudioFileClip(video_path)  # 读取视频
        sound_path = os.path.join(sound_dir_path, sound_name + '.wav')  # 拼接目录
        audio_clip.write_audiofile(sound_path)  # 写入音频文件
        print(f'{sound_path} 提取成功')


def add_sound_to_video():
    sound_paths = []
    for sound_name in os.listdir(sound_dir_path):
        if sound_name == '.DS_Store':
            continue
        sound_path = os.path.join(sound_dir_path, sound_name)
        sound_paths.append(sound_path)

    sound_path = random.choice(sound_paths)  # 随机读取一个
    for video_name in os.listdir(gen_video_dir_path):
        if video_name == '.DS_Store':
            continue
        video_path = os.path.join(gen_video_dir_path, video_name)  # 自己生成视频的路径
        video = VideoFileClip(video_path)
        video_time = video.duration  # 读取 自己视频的时间长度
        audio = AudioFileClip(sound_path)
        audio_video_time = audio.duration  # 音频的时间长度
        if audio_video_time > video_time:
            # 切割出目标视频长度的音频
            audio = audio.subclip(0, video_time)
        new_video = video.set_audio(audio)  # 加入音频
        save_path = os.path.join(gen_video_dir_path2, f"{video_name.split('.')[0]}-sound.mp4")
        new_video.write_videofile(save_path, threads=8)  # 写入保存的路径
        # 渐变
        gradient_path = os.path.join(gen_video_dir_path3, f"{video_name.split('.')[0]}-gradient.mp4")
        special_effects(save_path, gradient_path)
        video.close()
        audio.close()
        new_video.close()
        print(f'{save_path} 生成成功')

def special_effects(inputfile, outputfile):
    """
     将输入视频加工 成 特殊效果，开头结尾渐变效果
    :param inputfile:
    :param outputfile:
    :return:
    """
    video = VideoFileClip(inputfile)
    w, h = video.size
    subvideo = video.subclip(0, 8).fadein(4, (0.5, 1, 1))
    subvideo1 = video.subclip(8, video.duration - 6)
    subvideo2 = video.subclip(video.duration - 6).fadeout(2, (0, 0, 0))

    txt = TextClip('搞笑聊天', font='simhei.ttf', fontsize=40)
    final_clip = concatenate_videoclips([subvideo, subvideo1, subvideo2])
    painting_txt = (CompositeVideoClip([final_clip, txt.set_pos((w / 2, h - 100))]).set_duration(final_clip.duration))

    # w,h=subvideo1.size
    # subvideo1.mask.get_frame=lambda t:circle(screensize(subvideo1.w,subvideo1.h),center=(subvideo1.w/2,subvideo1.h/4),radius=max(0,int(800-200*t)),col1=1,col2=0,blur=4)
    # trans=ImageClip('mount.jpg').resize(video.size)
    # resultvideo=concatenate_videoclips([subvideo,subvideo1,subvideo2])
    # resultvideo.write_videofile(outputfile)
    painting_txt.write_videofile(outputfile)

def del_temp_file(path):
    """
    删除目录下的临时文件
    :param path:
    :return:
    """
    # 删除临时文件
    g = os.walk(path)

    for path, dir_list, file_list in g:
        print(path)
        for file_name in file_list:
            print(file_name)
            if file_name.startswith('temp'):
                os.remove(path +os.sep+file_name)

if __name__ == '__main__':
    create_dirs([gen_image_dir_path, gen_video_dir_path, clean_ocr_dir_path, sound_dir_path, gen_video_dir_path2])
    # 获取 orc json 格式对话数据
    # get_ocr_json(ocr_dir_path)
    # 开启浏览器 访问 fake-wechat-gen 项目
    # browser = get_browser()
    # 通过 orc json 和 自动微信聊天生成，并生成一批图片
    # gen_wechat_image(browser)
    # 通过生成的一批图片，生成视频
    # gen_video_from_image()
    # 从抖音下载的视频 转 音频
    get_sound_from_video()
    # 将音频添加到自己的视频中
    add_sound_to_video()
    #del_temp_file("./gen/")
