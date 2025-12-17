# coding = utf-8
"""
    @project: missionPlatform
    @Author：Waite0603
    @file： urls.py
    @date：2024/6/19 上午11:45
"""
from django.urls import re_path
from . import views as v

urlpatterns = [
  re_path(r'^register/?$', v.register, name='register'),
  re_path(r'^login/?$', v.login, name='login'),
  re_path(r'^userinfo/?$', v.user_info, name='get_user_info'),
  re_path(r'^update/?$', v.update_user_info, name='update_user_info'),
  re_path(r'^logout/?$', v.logout, name='logout'),
  re_path(r'^captcha/?$', v.get_verify_code, name='get_verify_code'),
  re_path(r'^contact/?$', v.contact_us, name='contact_us'),
  re_path(r'^contact/list/?$', v.get_feedback, name='get_feedback'),
  re_path(r'^avatar/upload/?$', v.upload_avatar, name='upload_avatar'),
  re_path(r'^avatar/preview/?$', v.preview_avatar, name='preview_avatar'),
  re_path(r'^vip/open/?$', v.open_vip, name='open_vip'),
  re_path(r'^vip/direct/open/?$', v.direct_open_vip, name='direct_open_vip'),
  re_path(r'^vip/code/create/?$', v.create_vip_code, name='create_vip_code'),
]
