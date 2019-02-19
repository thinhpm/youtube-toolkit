import pyforms
from pyforms.basewidget import BaseWidget
from pyforms.controls import ControlText
from pyforms.controls import ControlButton
from pyforms.controls import ControlCombo
from pyforms import settings as formSettings
import os
import subprocess

# formSettings.PYFORMS_STYLESHEET = 'css/style.css'

pwd = os.getcwd()


class YoutubeToolKit(BaseWidget):
    def __init__(self):
        super(YoutubeToolKit, self).__init__('Youtube ToolKit v1.0')

        self._accounts = ControlCombo('Please choose account')

        items_account = getDataInFolder('accounts', 'folder')

        for item in items_account:
            self._accounts.add_item(item, item)

        self._input_files = ControlCombo('Please choose video file')

        items_input_file = getDataInFolder('input', 'mp4')

        for item in items_input_file:
            self._input_files.add_item(item, item)

        self._ffmpeg_files = ControlCombo("Please choose file ffmpeg")

        items_ffmpeg = getDataInFolder('ffmpeg-files', 'txt')

        for item in items_ffmpeg:
            self._ffmpeg_files.add_item(item, item)

        self._title = ControlText("Title")
        self._description = ControlText("Description")
        self._tags = ControlText("Tags")


        self._button_upload = ControlButton('Upload')
        self._button_upload.value = self.__buttonUploadAction

    def __buttonUploadAction(self):
        data = {
            'title': self._title.value,
            'description': self._description.value,
            'tags': self._tags.value
        }

        output_file_name = processVideo(self._input_files.value, self._ffmpeg_files.value)

        uploadToYoutube(self._accounts.value, output_file_name, data)
        print("Done")


def getDataInFolder(folder, type):
    results = []
    file_list = os.listdir(pwd + '/' + folder)

    for file in file_list:
        if type != 'folder':
            if file.endswith(type):
                results.append(file)
        else:
            if file.endswith(''):
                results.append(file)

    return results


def processVideo(file_video, file_ffmpeg, stt = 0):
    print("process video...")
    path_file = pwd + '/ffmpeg-files/' + file_ffmpeg
    fo = open(path_file, "r")
    lines = fo.readlines()

    if len(lines) > 0:
        string_process = lines[0]
        string_process = string_process.replace("input.mp4", 'input/' + str(file_video))
        string_process = string_process.replace("output.mp4", "output/output" + str(stt) + ".mp4")
        os.system(string_process)

        return "output" + str(stt) + ".mp4"

    return False


def isFirstUpload(account):
    f = open(pwd + '/accounts/' + account + '/credentials.json', 'r')
    lines = f.readlines()
    f.close()

    if len(lines) == 0:
        return True

    return False


def upload_youtube_and_get_url(path_file_account, title, description, tags, file_upload):
    process = subprocess.Popen(['py', 'youtube-upload', '--title=' + str(title) + '', '--tags=' + str(tags)
                                + '', '--description=' + str(description)
                                + '', '--client-secrets=' + path_file_account + '/client_secrets.json',
                                '--credentials-file=' + path_file_account + '/credentials.json',
                                pwd + '/output/' + str(file_upload)], shell=True,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = process.communicate()
    print(stdout)
    return 'Video URL' in stdout


def uploadToYoutube(account, file_upload, data):
    print ("Uploading...")
    path_file_account = pwd + '/accounts/' + account

    if isFirstUpload(account):
        os.system('py youtube-upload --title="' + str(data['title'])
                  + '" --description="' + str(data['description'])
                  + '" --tags="' + str(data['tags'])
                  + '" --client-secrets=' + path_file_account + '/client_secrets.json --credentials-file='
                  + path_file_account + '/credentials.json '
                  + pwd + '/output/' + str(file_upload))
        print("Done upload")
        return ''
    else:
        check = upload_youtube_and_get_url(path_file_account, data['title'], data['description'], data['tags'], file_upload)

    return check


# Execute the application
if __name__ == "__main__":
    pyforms.start_app(YoutubeToolKit)
