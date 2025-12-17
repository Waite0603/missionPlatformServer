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
  category = request.GET.get('category')

  if category:
    course_list = Course.objects.filter(category=category, status__gt=0).order_by('-create_time').values()
  else:
    course_list = Course.objects.filter(status__gt=0).order_by('-create_time').values()

  # 添加分类名称
  for course in course_list:
    category_name = CourseCategory.objects.filter(id=course['category_id']).values()
    course['category'] = category_name[0]['name']

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
# 更改课程会员状态
def change_course_status(request):
  course_id = request.GET.get('id')

  if not all([course_id]):
    return ResponseInfo.fail(400, '参数不全')

  # 查看课程是否存在
  course_data = Course.objects.filter(id=course_id).first()

  if not course_data:
    return ResponseInfo.fail(404, '课程不存在')

  # 如果课程状态为1, 则更改为2
  if course_data.status == 1:
    Course.objects.filter(id=course_id).update(status=2)
  else:
    Course.objects.filter(id=course_id).update(status=1)

  return ResponseInfo.success('更改成功')


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
def preview_cover(request, cover_url):
  if not cover_url:
    return ResponseInfo.fail(400, '参数不全')

  cover_dir = 'upload/cover'

  try:
    return FileResponse(open(f'{cover_dir}/{cover_url}', 'rb'))
  except Exception as e:
    print(e)
    return ResponseInfo.fail(404, '文件不存在')


# 推荐课程
@get_only
def recommend_course(request):
  id = int(request.GET.get('id'))

  if not id:
    return ResponseInfo.fail(400, '参数不全')

  course_data = Course.objects.filter(id=id).first()

  if not course_data:
    return ResponseInfo.fail(404, '课程不存在')

  # 获取分类
  category = course_data.category

  # 获取推荐课程, 前四条, status!=0
  recommend_course_list = Course.objects.filter(category=category, status__gt=0).exclude(id=id).order_by(
    '-create_time')[:4]

  recommend_course_list = [
    model_to_dict(course) for course in recommend_course_list
  ]

  print(recommend_course_list)
  # 添加分类名称
  for course in recommend_course_list:
    category_name = CourseCategory.objects.filter(id=course['category_id']).values()
    course['category'] = category_name[0]['name']

  len_recommend_course_list = len(recommend_course_list)

  if len_recommend_course_list < 3:
    # 如果推荐课程不足3条, 补充其他课程
    other_course_list = Course.objects.filter(status__gt=0).exclude(id=id).exclude(category=category).order_by(
      '-create_time')[:3 - len_recommend_course_list]

    other_course_list = [
      model_to_dict(course) for course in other_course_list
    ]

    for course in other_course_list:
      category_name = CourseCategory.objects.filter(id=course['category_id']).values()
      course['category'] = category_name[0]['name']

    recommend_course_list.extend(other_course_list)

  return ResponseInfo.success('获取成功', data=recommend_course_list)


# 首页推荐课程
@get_only
def index_recommend_course(request):
  course_list = Course.objects.filter(status__gt=0).order_by('-create_time')[:6]

  data = []
  for course in course_list:
    course_dict = model_to_dict(course)
    course_dict['author'] = course.author.username
    # 添加分类名称
    category_name = CourseCategory.objects.filter(id=course.category_id).values()
    course_dict['category'] = category_name[0]['name']
    data.append(course_dict)

  return ResponseInfo.success('获取首页推荐课程成功', data)


# 搜索课程
@get_only
def search_course(request):
  keyword = request.GET.get('keyword')

  if not keyword:
    return ResponseInfo.fail(400, '参数不全')

  course_list = Course.objects.filter(name__contains=keyword, status__gt=0).order_by('-create_time').values()

  # 添加分类名称
  for course in course_list:
    category_name = CourseCategory.objects.filter(id=course['category_id']).values()
    course['category'] = category_name[0]['name']

  course_list = [
    model_to_dict(course) for course in course_list
  ]

  return ResponseInfo.success('搜索成功', data=course_list)
