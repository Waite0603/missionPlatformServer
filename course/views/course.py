# coding = utf-8
"""
    @project: missionPlatform
    @Author：Waite0603
    @file： course.py
    @date：2024/9/6 上午10:44
    
    TODO:
"""
import hashlib
import json
import os
import time

from django.http import FileResponse

from missionPlatform.decorators import get_only, post_only, login_required
from missionPlatform.utils.response import ResponseInfo
from missionPlatform.utils.token import get_user_info
from missionPlatform.utils.tools import model_to_dict
from ..models import Course, CourseCategory


@post_only
@login_required
def create_course(request):
  try:
    data = json.loads(request.body)
  except json.JSONDecodeError:
    return ResponseInfo.fail(400, 'Invalid JSON')

  name = data.get('name')
  desc = data.get('desc')
  cover = data.get('cover')
  category = data.get('category')

  if not all([name, desc, cover, category]):
    return ResponseInfo.fail(400, '参数不全')

  # 查看课程是否存在
  course_data = Course.objects.filter(name=name).first()
  if course_data:
    return ResponseInfo.fail(400, '课程已存在')

  # 查看分类是否存在
  category_data = CourseCategory.objects.filter(name=category).first()
  if not category_data:
    return ResponseInfo.fail(404, '分类不存在')

  # 创建课程
  Course.objects.create(
    name=name,
    desc=desc,
    cover=cover,
    category=category_data,
    author=get_user_info(request)
  )

  course_list = Course.objects.all().order_by('-create_time').values()

  course_list = [
    model_to_dict(course) for course in course_list
  ]
  return ResponseInfo.success('创建成功', data=course_list)


@get_only
def get_course_list(request):
  course_list = Course.objects.filter(status=1).order_by('-create_time').values()

  course_list = [
    model_to_dict(course) for course in course_list
  ]

  return ResponseInfo.success('获取成功', data=course_list)


@post_only
@login_required
def update_course(request):
  try:
    data = json.loads(request.body)
  except json.JSONDecodeError:
    return ResponseInfo.fail(400, 'Invalid JSON')

  course_id = data.get('id')

  if not course_id:
    return ResponseInfo.fail(400, '参数不全')

  # 查看课程是否存在
  course_data = Course.objects.filter(id=course_id).first()

  if not course_data:
    return ResponseInfo.fail(404, '课程不存在')

  name = data.get('name')
  desc = data.get('desc')
  cover = data.get('cover')
  category = data.get('category')

  # 查看分类是否存在
  category_data = CourseCategory.objects.filter(name=category).first()

  if not category_data:
    return ResponseInfo.fail(404, '分类不存在')

  # 有什么参数就更新什么参数
  update_data = {}
  if name:
    update_data['name'] = name
  if desc:
    update_data['desc'] = desc
  if cover:
    update_data['cover'] = cover
  if category:
    update_data['category'] = category_data

  Course.objects.filter(id=course_id).update(**update_data)

  course_data = Course.objects.filter(id=course_id).first()

  return ResponseInfo.success('更新成功', data=model_to_dict(course_data))


@get_only
@login_required
def delete_course(request):
  course_id = request.GET.get('id')

  if not course_id:
    return ResponseInfo.fail(400, '参数不全')

  # 查看课程是否存在
  course_data = Course.objects.filter(id=course_id).first()

  if not course_data:
    return ResponseInfo.fail(404, '课程不存在')

  Course.objects.filter(id=course_id).update(status=0)

  return ResponseInfo.success('删除成功')


# 上传课程封面
@post_only
@login_required
def upload_cover(request):
  user_data = get_user_info(request)

  file_obj = request.FILES.get('file')

  if not file_obj:
    return ResponseInfo.fail(400, '请上传封面')

  # 确定格式
  if file_obj.content_type not in ['image/jpeg', 'image/png']:
    return ResponseInfo.fail(400, '请上传jpg/png格式的图片')

  upload_dir = 'upload/cover'
  if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

  # 重命名封面, md5(用户名+时间戳)
  file_name = file_obj.name
  file_name = file_name.split('.')
  file_name = hashlib.md5((user_data.username + str(time.time())).encode('utf-8')).hexdigest() + '.' + file_name[-1]

  # 保存封面到 ./upload/cover
  try:
    with open(f'{upload_dir}/{file_name}', 'wb') as f:
      for chunk in file_obj.chunks():
        f.write(chunk)
  except Exception as e:
    print(e)
    return ResponseInfo.fail(500, '上传失败')

  return ResponseInfo.success('上传成功', data={'cover': f'{file_name}'})


# 预览封面
@get_only
def preview_cover(request):
  cover_url = request.GET.get('cover')

  if not cover_url:
    return ResponseInfo.fail(400, '参数不全')

  cover_dir = 'upload/cover'

  try:
    return FileResponse(open(f'{cover_dir}/{cover_url}', 'rb'))
  except Exception as e:
    print(e)
    return ResponseInfo.fail(404, '文件不存在')
