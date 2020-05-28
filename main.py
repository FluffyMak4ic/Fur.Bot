# -*- coding:utf-8 -*-
# programm: furbot
# description: furbot is a bot written for the VK social network in order to pump out pictures from the e926.net website.
# author: Mak4ic
# website: https://github.com/FluffyMak4ic/Fur.Bot

import requests
import json
import re
import vk_api
import urllib.parse
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from config import *

vk_session = vk_api.VkApi(token=vk_api_token)
e_downloader_session = requests.Session()
e_downloader_session.headers.update({'User-Agent': user_agent})

r_tab = "-------------------\n"

def write_msg(user_id, message):
    vk.messages.send(user_id=user_id, random_id=get_random_id(), message=message)

vk = vk_session.get_api()

upload = VkUpload(vk_session)  # Для загрузки изображений
longpoll = VkLongPoll(vk_session)
print("Bot starting!")
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        print('id{}: "{}"'.format(event.user_id, event.text), end=' ')
        if event.text == "Начать" or event.text == ".help":
            write_msg(event.user_id, 'Автор [id260228378|Максим Гусев]\n' + "Информация о боте: Furbot - это бот, созданный для социальной сети ВКонтакте, чтобы выкачивать картинки с сайта e926.net.\n" + "Команды:\n" + ".help - Все о боте\n" + ".loadposts - загрузить картинки")
        elif event.text == ".loadposts":
            write_msg(event.user_id, "Ведите номер страници")
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                    id_page = int(event.text)
                    if id_page >= 0 and id_page < 500:
                        try:
                            e_downloader_posts = e_downloader_session.get(url + "posts.json?page=" + str(id_page))
                            e_downloader_posts_json = json.loads(e_downloader_posts.text)
                        except Exception as e:
                            print("Exception:" + str(e))
                        attachments = []
                        write_msg(event.user_id, "Подождите ваш запрос обробатывается...")
                        for i in e_downloader_posts_json["posts"]:
                            if i["rating"] == "s":
                                id_img = str(i["id"])
                                rating_img = i["rating"]
                                tags_general_img = re.sub(r".['']", "", str(i["tags"]["general"])).rstrip("]")
                                tags_species_img = re.sub(r".['']", "", str(i["tags"]["species"])).rstrip("]")
                                tags_character_img = re.sub(r".['']", "", str(i["tags"]["character"])).rstrip("]")
                                tags_copyright_img = re.sub(r".['']", "", str(i["tags"]["copyright"])).rstrip("]")
                                tags_artist_img = re.sub(r".['']", "", str(i["tags"]["artist"])).rstrip("]")
                                tags_meta_img = re.sub(r".['']", "", str(i["tags"]["meta"])).rstrip("]")
                                description_img = i["description"]
                                url_img = i["file"]["url"]

                                if tags_character_img == "[":
                                    tags_character_img = ""
                                if tags_copyright_img == "[":
                                    tags_copyright_img = ""
                                if tags_artist_img == "[":
                                    tags_artist_img = ""
                                if tags_meta_img == "[":
                                    tags_meta_img = ""

                                image = e_downloader_session.get(url_img, stream=True)
                                photo = upload.photo_messages(photos=image.raw)[0]
                                attachments = []
                                attachments.append(
                                    'photo{}_{}'.format(photo['owner_id'], photo['id'])
                                )
                                '''vk.messages.send(user_id=event.user_id,random_id=get_random_id(),message="ID : " + id_img + "\n" + r_tab + "Rating: " + rating_img + "\n" + r_tab + "Tags general: " + tags_general_img + "\n" + r_tab + "Tags species: " + tags_species_img + "\n" + r_tab + "Tags character: " + tags_character_img + "\n" + r_tab + "Tags copyright: " + tags_copyright_img + "\n" + r_tab + "Tags artist: " + tags_artist_img + "\n" + r_tab + "Tags meta: " + tags_meta_img + "\n" + r_tab + "Description: " + description_img + "\n" + r_tab + "Url: " + url_img + r_tab)'''
                                vk.messages.send(user_id=event.user_id,attachment=','.join(attachments),random_id=get_random_id(),message="")
                        break
                    else:
                        write_msg(event.user_id, "Вы вели не верное число!")
                        break

        elif event.text == ".search":
            write_msg(event.user_id, "Ведите номер страници")
            for event in longpoll.listen():
                if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                    id_page = int(event.text)
                    if id_page >= 0 and id_page < 500:
                        write_msg(event.user_id, "Ведите желаемый запрос")
                        for event1 in longpoll.listen():
                            if event1.type == VkEventType.MESSAGE_NEW and event1.to_me and event1.text:
                                search_data = urllib.parse.quote_plus(event1.text)
                                if search_data:
                                    break
                                    
                        try:
                            e_downloader_posts = e_downloader_session.get(url + "posts.json?page=" + str(id_page) + "&tags=" + search_data)
                            e_downloader_posts_json = json.loads(e_downloader_posts.text)
                        except Exception as e:
                            print("Exception:" + str(e))
                        attachments = []
                        write_msg(event.user_id, "Подождите ваш запрос обробатывается...")
                        for i in e_downloader_posts_json["posts"]:
                            if i["rating"] == "s":
                                id_img = str(i["id"])
                                rating_img = i["rating"]
                                tags_general_img = re.sub(r".['']", "", str(i["tags"]["general"])).rstrip("]")
                                tags_species_img = re.sub(r".['']", "", str(i["tags"]["species"])).rstrip("]")
                                tags_character_img = re.sub(r".['']", "", str(i["tags"]["character"])).rstrip("]")
                                tags_copyright_img = re.sub(r".['']", "", str(i["tags"]["copyright"])).rstrip("]")
                                tags_artist_img = re.sub(r".['']", "", str(i["tags"]["artist"])).rstrip("]")
                                tags_meta_img = re.sub(r".['']", "", str(i["tags"]["meta"])).rstrip("]")
                                description_img = i["description"]
                                url_img = i["file"]["url"]

                                if tags_character_img == "[":
                                    tags_character_img = ""
                                if tags_copyright_img == "[":
                                    tags_copyright_img = ""
                                if tags_artist_img == "[":
                                    tags_artist_img = ""
                                if tags_meta_img == "[":
                                    tags_meta_img = ""

                                image = e_downloader_session.get(url_img, stream=True)
                                photo = upload.photo_messages(photos=image.raw)[0]
                                attachments = []
                                attachments.append(
                                    'photo{}_{}'.format(photo['owner_id'], photo['id'])
                                )
                                '''vk.messages.send(user_id=event.user_id,random_id=get_random_id(),message="ID : " + id_img + "\n" + r_tab + "Rating: " + rating_img + "\n" + r_tab + "Tags general: " + tags_general_img + "\n" + r_tab + "Tags species: " + tags_species_img + "\n" + r_tab + "Tags character: " + tags_character_img + "\n" + r_tab + "Tags copyright: " + tags_copyright_img + "\n" + r_tab + "Tags artist: " + tags_artist_img + "\n" + r_tab + "Tags meta: " + tags_meta_img + "\n" + r_tab + "Description: " + description_img + "\n" + r_tab + "Url: " + url_img + r_tab)'''
                                vk.messages.send(user_id=event.user_id,attachment=','.join(attachments),random_id=get_random_id(),message="")
                        break
                    else:
                        write_msg(event.user_id, "Вы вели не верное число!")
                        break    
        else:
            write_msg(event.user_id, "Вы вели неверную комманду. Что бы посмотреть все комманды напишите .help")
