import os
import re
import time

from django.shortcuts import render

# Create your views here.
# 上传视频
from django.http import JsonResponse, FileResponse, StreamingHttpResponse

from missionPlatform.decorators import post_only, login_required
from missionPlatform.utils.token import get_user_info
from missionPlatform.utils.tools import model_to_dict
# from video.models import Video, Category, UploadRecord
from missionPlatform.utils.response import ResponseInfo
import hashlib

from video.models import UploadRecord


@post_only
@login_required
def upload_video(request):
  """
  上传视频
  :param request:
  :return:
  """
  user_data = get_user_info(request)

  file_obj = request.FILES.get('file')
  print(file_obj.name)

  if not file_obj:
    return ResponseInfo.fail(400, '请上传视频')

  upload_dir = 'upload/video'
  if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

  # 获取视频类型, 视频大小
  video_type = file_obj.content_type
  video_size = file_obj.size

  # 重命名视频, md5(用户名+时间戳)
  file_name = file_obj.name
  file_name = file_name.split('.')
  file_name = hashlib.md5((user_data.username + str(time.time())).encode('utf-8')).hexdigest() + '.' + file_name[-1]

  # 保存视频到 ./upload/video
  try:
    with open(f'{upload_dir}/{file_name}', 'wb') as f:
      for chunk in file_obj.chunks():
        f.write(chunk)
  except Exception as e:
    print(e)
    return ResponseInfo.fail(500, '上传失败')

  # 保存上传记录
  upload_record = UploadRecord.objects.create(
    name=file_name,
    path=f'{upload_dir}/{file_name}',
    size=video_size,
    format=video_type,
    author=user_data
  )

  # 格式化输出 upload_record
  data = model_to_dict(upload_record)

  return ResponseInfo.success('上传成功', data=data)


def get_video(request, video_path):
  """
  观看视频
  :param request:
  :param video_path: 视频路径
  :return:
  """
  file_path = os.path.join('upload/video', video_path)
  if not os.path.exists(file_path):
    return ResponseInfo.fail(400, '视频不存在')

  file_size = os.path.getsize(file_path)
  range_header = request.headers.get('Range', '').strip()
  range_match = re.match(r'bytes=(\d+)-(\d*)', range_header)

  if range_match:
    first_byte, last_byte = range_match.groups()
    first_byte = int(first_byte) if first_byte else 0
    last_byte = int(last_byte) if last_byte else file_size - 1
    length = last_byte - first_byte + 1
    response = StreamingHttpResponse(file_iterator(file_path, first_byte, length), status=206)
    response['Content-Range'] = f'bytes {first_byte}-{last_byte}/{file_size}'
  else:
    response = StreamingHttpResponse(file_iterator(file_path))

  response['Accept-Ranges'] = 'bytes'
  response['Content-Type'] = 'video/mp4'
  response['Content-Disposition'] = 'inline'
  return response


# 文件迭代器, 视频流分段传输
def file_iterator(file_name, offset=0, length=None, chunk_size=8192):
  with open(file_name, 'rb') as f:
    f.seek(offset, os.SEEK_SET)
    remaining = length
    while remaining is None or remaining > 0:
      chunk_size = min(chunk_size, remaining) if remaining else chunk_size
      data = f.read(chunk_size)
      if not data:
        break
      if remaining:
        remaining -= len(data)
      yield data
