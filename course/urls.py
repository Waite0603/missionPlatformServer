# coding = utf-8
"""
    @project: missionPlatform
    @Author：Waite0603
    @file： urls.py
    @date：2024/9/6 上午10:44
    
    TODO:
"""
from django.urls import re_path
from .views import course_category as category
from .views import course_chapter as chapter
from .views import course

urlpatterns = [
  re_path(r'^category/create/?$', category.create_category, name='create_category'),
  re_path(r'^category/list/?$', category.get_category_list, name='get_category_list'),
  re_path(r'^category/update/?$', category.update_category, name='update_category'),
  re_path(r'^category/delete/?$', category.delete_category, name='delete_category'),

  re_path(r'^create/?$', course.create_course, name='create_course'),
  re_path(r'^list/?$', course.get_course_list, name='get_course_list'),
  re_path(r'^update/?$', course.update_course, name='update_course'),
  re_path(r'^change/status/?$', course.change_course_status, name='update_course_status'),
  re_path(r'^delete/?$', course.delete_course, name='delete_course'),
  re_path(r'^upload/cover/?$', course.upload_cover, name='upload_cover'),
  re_path(r'^cover/(?P<cover_url>.+)$', course.preview_cover, name='get_cover'),
  re_path(r'^recommend/?$', course.recommend_course, name='recommend_course'),
  re_path(r'^index/?$', course.index_recommend_course, name='index_recommend_course'),
  re_path(r'^search/?$', course.search_course, name='search_course'),

  re_path(r'^chapter/create/?$', chapter.create_chapter, name='create_chapter'),
  re_path(r'^chapter/list/?$', chapter.get_chapter_list, name='get_chapter_list'),
  re_path(r'^chapter/update/?$', chapter.update_chapter, name='update_chapter'),
  re_path(r'^chapter/delete/?$', chapter.delete_chapter, name='delete_chapter'),

]
