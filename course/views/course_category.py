# coding = utf-8
"""
    @project: missionPlatform
    @Author：Waite0603
    @file： course_category.py
    @date：2024/9/6 上午10:54
    
    TODO:
"""
import json

from missionPlatform.decorators import get_only, post_only, login_required
from missionPlatform.utils.response import ResponseInfo
from missionPlatform.utils.token import get_user_info
from missionPlatform.utils.tools import model_to_dict
from ..models import CourseCategory


@post_only
@login_required
def create_category(request):
  try:
    data = json.loads(request.body)
  except json.JSONDecodeError:
    return ResponseInfo.fail(400, 'Invalid JSON')

  name = data.get('name')
  desc = data.get('desc')

  if not name or not desc:
    return ResponseInfo.fail(400, '参数不全')

  # 查看分类是否存在
  category_data = CourseCategory.objects.filter(name=name).first()
  if category_data:
    return ResponseInfo.fail(400, '分类已存在')

  # 创建分类
  CourseCategory.objects.create(
    name=name,
    desc=desc
  )

  # 返回所有分类
  category_list = CourseCategory.objects.all().order_by('-create_time').values()

  category_list = [
    model_to_dict(category) for category in category_list
  ]

  return ResponseInfo.success('创建成功', data=category_list)


@get_only
def get_category_list(request):
  category_list = CourseCategory.objects.all().order_by('-create_time').values()

  category_list = [
    model_to_dict(category) for category in category_list
  ]

  return ResponseInfo.success('获取成功', data=category_list)


@post_only
@login_required
def update_category(request):
  try:
    data = json.loads(request.body)
  except json.JSONDecodeError:
    return ResponseInfo.fail(400, 'Invalid JSON')

  category_id = data.get('id')
  name = data.get('name')
  desc = data.get('desc')

  if not category_id or not name or not desc:
    return ResponseInfo.fail(400, '参数不全')

  # 查看分类是否存在
  category_data = CourseCategory.objects.filter(id=category_id).first()
  if not category_data:
    return ResponseInfo.fail(400, '分类不存在')

  # 更新分类
  category_data.name = name
  category_data.desc = desc
  category_data.save()

  # 返回所有分类
  category_list = CourseCategory.objects.all().order_by('-create_time').values()

  category_list = [
    model_to_dict(category) for category in category_list
  ]

  return ResponseInfo.success('更新成功', data=category_list)


@get_only
def delete_category(request):
  category_id = request.GET.get('id')

  if not category_id:
    return ResponseInfo.fail(400, '参数不全')

  # 查看分类是否存在
  category_data = CourseCategory.objects.filter(id=category_id).first()
  if not category_data:
    return ResponseInfo.fail(400, '分类不存在')

  # 删除分类
  category_data.delete()

  # 返回所有分类
  category_list = CourseCategory.objects.all().order_by('-create_time').values()

  category_list = [
    model_to_dict(category) for category in category_list
  ]

  return ResponseInfo.success('删除成功', data=category_list)

# 上傳視頻文件