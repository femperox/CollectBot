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
        tmp_dict = json.load(open('./privates.json', 'r')) # с файолм
        self.__group_id = tmp_dict['group_id']
        self.__user_token = tmp_dict['access_token']
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

    def _get_topic_by_name(self, topic_name: str) -> int:
        """
        Args:
            topic_name (str): Название обсуждения

        Returns:
            int: ID обсуждения с именем topic_name или -1
        """
        try:
            vk_response = self.vk.board.getTopics(group_id=self.__group_id, preview_length=0)
            topics = vk_response.get('items', [])
            for topic in topics:
                if topic['title'] == topic_name:
                    return topic['id']
        except:
            return -1
        
    def _get_previous_attachments(self, topic_id: int, comm_id: int) -> str:
        """Получить старые вложения изменяемого комментария

        Args:
            topic_id (int): ID обсуждения
            comm_id (int): ID комментария

        Returns:
            (str): Пустая строка или строка, содержащая вложения Вконтакте, разделённые запятыми
        """
        result = ''
        try:
            comment = self.vk.board.getComments(
                group_id=self.__group_id,
                topic_id=topic_id,
                need_likes=0,
                start_comment_id=comm_id,
                count=1,
                extended=1
            )['items'][0]
            comm_attachments = comment.get('attachments', [])
            for attachment in comm_attachments:
                att_photo = attachment.get('photo', {})
                result += 'photo{}_{},'.format(att_photo.get('owner_id', ''), att_photo.get('id', ''))
            if result != '':
                if result[len(result) - 1] == ',':
                    result[:len(result) - 1:]
            return result
        except:
            print_exc()
            return ''
    
    def post_comment(self, topic_name: str, message: str, comment_url='', from_group=1, img_urls=[]) -> str:
        """Позволяет создать или изменить комментарий в обсуждении. Для изменения нужно передать ссылку на комментарий

        Args:
            topic_name (str): Название обсуждения
            message (str): Текст комментария
            comment_url (str, optional): url комментария в обсуждении. Передаётся в случае изменения. По умолчанию = ''
            from_group (int, optional): От имени кого будет опубликована запись. 1 - от сообщества, 0 - от имени пользователя. По умолч. = 1
            img_urls (list, optional): Список url картинок, которые необходимо прикрепить. По умолчанию = [].

        Returns:
            str: Возвращает url созданного / изменённого комментария
        """
        try:
            topic_id = self._get_topic_by_name(topic_name)
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
            
            if comment_url == '':
                comm_id = self.vk.board.createComment(**params)
            else:
                params.pop('guid')
                params.pop('from_group')
                comm_id = int(comment_url[comment_url.find('post=') + 5:])
                if attachments == '':
                    attachments = self._get_previous_attachments(topic_id, comm_id)
                    if attachments != '':
                        params.setdefault('attachments', attachments)
                params.setdefault('comment_id', comm_id)
                if not self.vk.board.editComment(**params):
                    return ''
        
            res_url = 'https://vk.com/topic-{}_{}?post={}'.format(self.__group_id, topic_id, comm_id)
            return res_url
        except:
            print_exc()
            return ''
    
    def get_active_comments_users_list(self, post_url: str) -> tuple:
        """Получает список ссылок на страницы пользователей, прокомментировавших пост

        Args:
            post_url (str): Ссылка на пост

        Returns:
            tuple: Возвращает кортеж из списка пользователей и ссылки на пост
        """
        counter = 1
        try:
            post_id = int(post_url[post_url.rfind('_') + 1:])
            admin_ids = set([contact['user_id'] for contact in self.vk.groups.getById(
                    group_ids=self.__group_id, 
                    fields='contacts'
            )[0]['contacts']])
            user_ids = set()
            commentators = []
            last_comment_id = -1
            while (counter == 1 or len(commentators)):
                params = {
                    'owner_id': -int(self.__group_id),
                    'post_id': post_id,
                    'count': 100,
                    'extended': 1,
                    'fields': 'id,first_name,last_name'
                }
                if counter > 1:
                    params.setdefault('start_comment_id', last_comment_id)
                    params.setdefault('offset', 1)
                commentators = self.vk.wall.getComments(**params).get('profiles', [])
                counter += 1
                for comm in commentators:
                    if comm['id'] > 0 and comm['id'] not in admin_ids:
                        new_tuple = (comm['id'], comm['first_name'] + ' ' + comm['last_name'])
                        user_ids.add(new_tuple)
                if commentators != []:
                    last_comment_id = commentators[len(commentators) - 1]['id']
            result = []
            for user_id in user_ids:
                result.append(('https://vk.com/id' + str(user_id[0]), user_id[1]))
            return result, post_url
        except:
            print_exc()
            return [], post_url