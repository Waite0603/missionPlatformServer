import hashlib
import json
import os
import time

from django.http import FileResponse

from missionPlatform.decorators import post_only, get_only, login_required
from django.db.models import Q
from django.contrib.auth.hashers import make_password
from missionPlatform.utils.response import ResponseInfo
from django.contrib.auth.hashers import check_password
from django.utils import timezone

from missionPlatform.utils.token import create_jwt_pair_for_user, get_user_info
from missionPlatform.utils.tools import model_to_dict
from .models import UserProfileModel, Contact, VipCode
import re


@post_only
def register(request):
  """
  用户注册
  :param request:
  :return:
  """
  try:
    data = json.loads(request.body)
  except json.JSONDecodeError:
    return ResponseInfo.fail(400, 'Invalid JSON')

  username = data.get('username')
  password = data.get('password')
  email = data.get('email')
  phone = data.get('phone')
  verify_code = data.get('verificationCode')

  # 2. 参数校验
  if not all([username, password, email, phone, verify_code]):
    return ResponseInfo.fail(400, '参数不全')

  # 校验邮箱格式
  if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
    return ResponseInfo.fail(400, '邮箱格式错误')

  # 校验手机号格式
  if not re.match(r'^1[3-9]\d{9}$', phone):
    return ResponseInfo.fail(400, '手机号格式错误')

  # 校验验证码
  if verify_code != '123456':
    return ResponseInfo.fail(400, '验证码错误')

  # 请求数据库，校验用户名、邮箱或手机号是否存在
  user_data = UserProfileModel.objects.filter(
    Q(username=username) | Q(email=email) | Q(phone=phone)
  ).first()

  if user_data:
    if user_data.username == username:
      return ResponseInfo.fail(400, '用户名已存在')
    elif user_data.email == email:
      return ResponseInfo.fail(400, '邮箱已存在')
    elif user_data.phone == phone:
      return ResponseInfo.fail(400, '手机号已存在')

  # 密码加密
  password = make_password(password)

  UserProfileModel.objects.create(username=username, password=password, email=email, phone=phone,
                                  last_login=timezone.now())

  return ResponseInfo.success('注册成功')


@post_only
def login(request):
  """
  用户登录
  :param request:
  :return:
  """
  try:
    data = json.loads(request.body)
  except json.JSONDecodeError:
    return ResponseInfo.fail(400, 'Invalid JSON')

  username = data.get('username')
  password = data.get('password')
  # 2. 参数校验
  if not all([username, password]):
    return ResponseInfo.fail(400, '参数不全')
  # 3. 业务处理
  # 请求数据库，校验用户名和密码
  user_data = UserProfileModel.objects.filter(username=username).first()
  if not user_data or not check_password(password, user_data.password):
    return ResponseInfo.fail(401, '用户名或密码错误')

  # 查询结果转换为字典
  token = create_jwt_pair_for_user(user_data)
  user_data = model_to_dict(user_data)

  # 删除密码
  del user_data['password']
  del user_data['is_staff']
  user_data['token'] = token

  # 更新登录时间
  UserProfileModel.objects.filter(username=username).update(last_login=timezone.now())

  return ResponseInfo.success('登录成功', data=user_data)


@login_required
def logout(request):
  return ResponseInfo.success('登出成功')


# 获取验证码
@get_only
def get_verify_code(request):
  return ResponseInfo.success('123456')


# 获取用户信息
@get_only
@login_required
def user_info(request):
  user_data = get_user_info(request)

  user_data = model_to_dict(user_data)
  del user_data['password']

  return ResponseInfo.success('获取成功', user_data)


# 更新用户信息
@post_only
@login_required
def update_user_info(request):
  user_data = get_user_info(request)

  try:
    data = json.loads(request.body)
  except json.JSONDecodeError:
    return ResponseInfo.fail(400, 'Invalid JSON')

  email = data.get('email')
  phone = data.get('phone')
  password = data.get('password')
  first_name = data.get('firstName')
  last_name = data.get('lastName')
  birthday = data.get('birthday')
  address = data.get('address')
  sex = data.get('sex')

  update_fields = {}
  if email:
    update_fields['email'] = email
  if phone:
    update_fields['phone'] = phone
  if password:
    update_fields['password'] = make_password(password)
  if first_name:
    update_fields['first_name'] = first_name
  if last_name:
    update_fields['last_name'] = last_name
  if birthday:
    update_fields['birthday'] = birthday
  if address:
    update_fields['address'] = address
  if sex:
    update_fields['sex'] = sex

  # Update fields in a single call
  UserProfileModel.objects.filter(id=user_data.id).update(**update_fields)

  user_data = UserProfileModel.objects.filter(id=user_data.id).first()
  user_data = model_to_dict(user_data)

  del user_data['password']

  return ResponseInfo.success('更新成功', user_data)


# 上传头像
@post_only
@login_required
def upload_avatar(request):
  user_data = get_user_info(request)

  file = request.FILES.get('file')

  if not file:
    return ResponseInfo.fail(400, '文件不能为空')

  # 重命名文件, md5(用户名+时间戳)
  file_name = file.name
  file_name = file_name.split('.')
  file_name = hashlib.md5((user_data.username + str(time.time())).encode('utf-8')).hexdigest() + '.' + file_name[-1]

  # 保存文件到 ./upload/avatar
  upload_dir = 'upload/avatar'
  if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)

  try:
    with open(f'{upload_dir}/{file_name}', 'wb') as f:
      for chunk in file.chunks():
        f.write(chunk)
  except Exception as e:
    print(e)
    return ResponseInfo.fail(500, '上传失败')

  # 更新用户头像
  UserProfileModel.objects.filter(id=user_data.id).update(avatar=f'{file_name}')

  user_data = UserProfileModel.objects.filter(id=user_data.id).first()

  user_data = model_to_dict(user_data)

  del user_data['password']

  return ResponseInfo.success('上传成功', user_data)


# 预览头像
@get_only
def preview_avatar(request):
  avatar_url = request.GET.get('avatar')
  if not avatar_url:
    return ResponseInfo.fail(400, '参数不全')

  avatar_dir = 'upload/avatar'
  try:
    return FileResponse(open(f'{avatar_dir}/{avatar_url}', 'rb'))
  except FileNotFoundError:
    return ResponseInfo.fail(404, '文件不存在')


# 联系我们
@post_only
def contact_us(request):
  try:
    data = json.loads(request.body)
  except json.JSONDecodeError:
    return ResponseInfo.fail(400, 'Invalid JSON')

  name = data.get('name')
  email = data.get('email')
  message = data.get('message')

  # 2. 参数校验
  if not all([name, email, message]):
    return ResponseInfo.fail(400, '参数不全')

  # 校验邮箱格式
  if not re.match(r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$', email):
    return ResponseInfo.fail(400, '邮箱格式错误')

  # 保存数据
  Contact.objects.create(name=name, email=email, message=message)

  return ResponseInfo.success('提交成功, 我们会尽快联系您')


# 获取所有反馈
@get_only
@login_required
def get_feedback(request):
  user_data = get_user_info(request)

  user_data = UserProfileModel.objects.filter(id=user_data.id).first()

  feedback_data = Contact.objects.all().values()

  feedback_list = [
    model_to_dict(feedback) for feedback in feedback_data
  ]

  return ResponseInfo.success('获取成功', feedback_list)


# 开通会员
@post_only
@login_required
def open_vip(request):
  user_data = get_user_info(request)

  try:
    data = json.loads(request.body)
  except json.JSONDecodeError:
    return ResponseInfo.fail(400, 'Invalid JSON')

  vip_code = data.get('vipCode')

  if not vip_code:
    return ResponseInfo.fail(400, '参数不全')

  # 请求数据库，校验激活码是否存在
  vip_data = VipCode.objects.filter(code=vip_code, status=1).first()

  if not vip_data:
    return ResponseInfo.fail(400, '激活码无效')

  # 更新激活码状态
  VipCode.objects.filter(code=vip_code).update(status=0, active_time=timezone.now(), active_user=user_data)

  # 更新用户状态, 1- 1年会员, 10-永久会员
  if vip_data.type == 1:
    UserProfileModel.objects.filter(id=user_data.id).update(status=1, vip_start_time=timezone.now(),
                                                            vip_end_time=timezone.now() + timezone.timedelta(days=365))
  elif vip_data.type == 10:
    UserProfileModel.objects.filter(id=user_data.id).update(status=10, vip_start_time=timezone.now(),
                                                            vip_end_time=None)

  user_data = UserProfileModel.objects.filter(id=user_data.id).first()

  user_data = model_to_dict(user_data)

  del user_data['password']

  return ResponseInfo.success('开通成功', user_data)


# 创建会员激活码
@post_only
@login_required
def create_vip_code(request):
  user_data = get_user_info(request)

  try:
    data = json.loads(request.body)
    vip_type = data.get('type')
  except json.JSONDecodeError:
    return ResponseInfo.fail(400, 'Invalid JSON')

  # 随机生成激活码
  code = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()[:16]

  user_data = UserProfileModel.objects.filter(id=user_data.id).first()

  if user_data.status != 100:
    return ResponseInfo.fail(400, '权限不足')

  # 校验是否已存在
  while VipCode.objects.filter(code=code).first():
    code = hashlib.md5(str(time.time()).encode('utf-8')).hexdigest()[:16]

  # 保存数据
  VipCode.objects.create(code=code, type=vip_type)

  return ResponseInfo.success('创建成功', {'code': code})


# 直接开通会员
@post_only
@login_required
def direct_open_vip(request):
  user_data = get_user_info(request)

  try:
    data = json.loads(request.body)
    vip_type = data.get('vip_type')
    print(data)
  except json.JSONDecodeError:
    return ResponseInfo.fail(400, 'Invalid JSON')

  # 更新用户状态, 5- 1年会员, 10-永久会员
  user_data = UserProfileModel.objects.filter(id=user_data.id).first()
  if vip_type == 5:
    # 查看用户是否已经是会员
    if user_data.status == 5:
      UserProfileModel.objects.filter(id=user_data.id).update(
        vip_end_time=user_data.vip_end_time + timezone.timedelta(days=365))
    else:
      UserProfileModel.objects.filter(id=user_data.id).update(status=vip_type, vip_start_time=timezone.now(),
                                                              vip_end_time=timezone.now() + timezone.timedelta(
                                                                days=365))
  elif vip_type == 10:
    UserProfileModel.objects.filter(id=user_data.id).update(status=vip_type, vip_start_time=timezone.now(),
                                                            vip_end_time=None)

  user_data = UserProfileModel.objects.filter(id=user_data.id).first()

  user_data = model_to_dict(user_data)

  del user_data['password']

  return ResponseInfo.success('开通成功', user_data)
