from requests.api import request
import vk_api
from pprint import pprint
from traceback import print_exc
import requests
import os
import random
import json

class BoardBot:

    def __init__(self) -> None:
        tmp_dict = json.load(open('./privates.json', 'r'))
        self.__group_id = tmp_dict['group_id']
        self.__user_token = tmp_dict['access_token']
        self.__topic_id = tmp_dict['topic_id']

        self.__vk_session = vk_api.VkApi(
            token=self.__user_token
        )
        self.vk = self.__vk_session.get_api()
        self._init_tmp_dir()
    
    def _init_tmp_dir(self) -> None:
        if not os.path.isdir('./tmp'):
            os.mkdir('./tmp')

    def _get_image_extension(self, url):
        extensions = ['.png', '.jpg', '.jpeg', '.gif']
        for ext in extensions:
            if ext in url:
                return ext
        return '.jpg'

    def _local_image_upload(self, url: str) -> str:
        """Функция скачивает изображение по url и возвращает строчку с полученным именем файла

        Args:
            url (str): Ссылка на изображение

        Returns:
            str: Имя файла или пустая строка
        """
        try:
            extention = self._get_image_extension(url)
            filename = ''
            if extention != '':
                filename = 'new_image' + extention
                response = requests.get(url)
                image = open('./tmp/' + filename, 'wb')
                image.write(response.content)
                image.close()
            return filename
        except:
            return ''
    
    def _vk_image_upload(self, image_name: str) -> dict:
        """Загружает локальное изображение на сервера Вконтакте

        Args:
            image_name (str): Имя файла с изображением

        Returns:
            dict: В случае успешного выполнения запроса вернёт словарь с представлением медиа Вконтакте
        """
        if image_name != '':
            vk_response = self.vk.photos.getWallUploadServer(
                group_id=self.__group_id
            )
            vk_url = vk_response['upload_url']
            try:
                vk_response = requests.post(
                    vk_url, 
                    files={'photo': open('./tmp/{}'.format(image_name), 'rb')}
                ).json()
                os.remove('./tmp/' + image_name)
                if vk_response['photo']:
                    vk_image = self.vk.photos.saveWallPhoto(
                        group_id=self.__group_id,
                        photo=vk_response['photo'],
                        server=vk_response['server'],
                        hash=vk_response['hash']
                    )
                    return vk_image[0]
            except:
                print_exc()
                return {}
        return {}

    def _form_images_request_signature(self, image_urls: list) -> str:
        """Получает строку для опубликования медиа-вложений

        Args:
            image_urls (list): Список url-ссылок на изображения

        Returns:
            str:  Возвращает пустую строку или строку вида <type><owner_id>_<media_id>
        """
        result = ''
        urls_count = len(image_urls)
        for i in range(urls_count):
            new_image = self._local_image_upload(image_urls[i])
            if new_image != '':
                vk_image = self._vk_image_upload(new_image)
                if vk_image != {}:
                    result += 'photo{}_{}'.format(vk_image['owner_id'], vk_image['id']) + ('' if i == urls_count - 1 else ',')
        if result != '':
            if result[len(result) - 1] == ',':
                result[:len(result) - 1:]
        return result

    def get_topic_id(self): # Временное явление
        return self.__topic_id
    
    def post_comment(self, topic_id: int, message: str, from_group=1, img_urls=[]) -> int:
        """Запостить комментарий в обсуждение

        Args:
            topic_id (int): ID топика
            message (str): Текст комментария
            from_group (int, optional): От имени группы - 1 (по умолчанию), от имени владельца ключа доступа - 0
            img_urls (list, optional): Список url-ссылок на прикладываемые изображения. По умолчанию пустой список

        Returns:
            int: Возвращает ID созданного комментария в случае успеха и -1 в иных случаях
        """
        try:
            params = {
                'group_id': self.__group_id,
                'topic_id': topic_id,
                'message': message,
                'from_group': from_group,
                'guid': random.randint(0, 1000000000),
            }
            attachments = self._form_images_request_signature(img_urls)
            if attachments != '':
                params.setdefault('attachments', attachments)
            comm_id = self.vk.board.createComment(**params)
            return comm_id
        except:
            print_exc()
            return -1

b = BoardBot()
b.post_comment(b.get_topic_id(), ')))))', img_urls=[
    # 'https://images.ru.prom.st/816121682_w640_h640_yakortsy-stelyuschiesya-tribulus-trava.jpg',
    # 'https://lh3.googleusercontent.com/proxy/FaN_imi61_6uGs5GaMPLqKaw-ikTX1SCAQdhaV5tEnSUK0-21eRs07lLXyQiw4L0IDsbGplstzjC64it6bq_dTICsnzV6XiFOIKLrXL4rfqWM9cl4TsQNmyKb6Q'
    'https://i.ytimg.com/an_webp/2YJgQOqjOh4/mqdefault_6s.webp?du=3000&sqp=CML01ogG&rs=AOn4CLBpd7bZr79fAT6QudEeoMJdF8ztvA'
])
