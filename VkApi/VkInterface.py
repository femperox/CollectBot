import vk_api
from pprint import pprint
from traceback import print_exc
import requests
import os
import random
import json
import re
import time
from datetime import datetime

class BoardBot:

    def __init__(self) -> None:
        tmp_dict = json.load(open('./VkApi/privates.json', encoding='utf-8'))
        self.__group_id = tmp_dict['group_id']
        auth_data = self._login_pass_get(tmp_dict)
        if auth_data[0] and auth_data[1]:
            self.__vk_session = vk_api.VkApi(
                auth_data[0],
                auth_data[1],
                auth_handler=self._two_factor_auth
            )
        self.__vk_session.auth(token_only=True)
        self.vk = self.__vk_session.get_api()
        self._init_tmp_dir()

        self.lang = 100
    
    def _init_tmp_dir(self) -> None:
        if not os.path.isdir('tmp'):
            os.mkdir('tmp')

    def _two_factor_auth(self):
        key = input("Enter authentication code: ")
        remember_device = True
        return key, remember_device

    def _create_encrypt_key(self, privates: dict) -> str:
        """Создаёт или получает ключ для шифрования / дешифрования

        Args:
            privates (dict): json-словарь из файла с настройками доступа

        Returns:
            str: Ключ или ''
        """
        try:
            if privates.get('secret_key', '') == '':
                size = random.randint(5, 10)
                key = ''
                for _ in range(size):
                    key += chr(random.randint(0, 10000))
                privates.setdefault('secret_key', key)
                json.dump(privates, open('./VkApi/privates.json', 'w'))
            return privates.get('secret_key', '')
        except:
            print_exc()
            return ''
    
    def _encode_decode_str(self, key: str, string: str, encode=True) -> str:
        """Кодирует или декодирует строку по ключу

        Args:
            key (str): Ключ
            string (str): Строка для кодирования / декодирования
            encode (bool, optional): При encode=True - кодирует, иначе декодирует string

        Returns:
            str: Кодированое или декодированное значение string 
        """
        try:
            result = ''
            sign = 1 if encode else -1
            if key:
                counter = 0
                for char in string:
                    if counter == len(key):
                        counter = 0
                    result += chr(ord(char) + ord(key[counter]) * sign)
                    counter += 1
            return result
        except:
            print_exc()
            return ''
    
    def _login_pass_get(self, privates: dict) -> tuple:
        """Получает пару логин и пароль Вконтакте из файла настроек доступа

        Args:
            privates (dict): Настройки доступа

        Returns:
            tuple: Пара - логин и пароль или (None, None)
        """
        try:
            login = privates.get('login', '')
            password = privates.get('password', '')
            key = self._create_encrypt_key(privates)
            privates.setdefault('secret_key', key)
            if login == '' and password == '':
                # Поменять по надобности
                # ======================
                print('login:')
                new_login = input()
                print('password:')
                new_pass = input()
                # ======================
                login = self._encode_decode_str(key, new_login)
                password = self._encode_decode_str(key, new_pass)
                privates.setdefault('login', login)
                privates.setdefault('password', password)

                json.dump(privates, open('./VkApi/privates.json', 'w'))
                return new_login, new_pass
            new_login = self._encode_decode_str(key, login, encode=False)
            new_pass = self._encode_decode_str(key, password, encode=False)
            return new_login, new_pass
        except:
            print_exc()
            return None, None


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
                image = open('./VkApi/tmp/' + filename, 'wb')
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
                    files={'photo': open('./VkApi/tmp/{}'.format(image_name), 'rb')}
                ).json()
                os.remove('./VkApi/tmp/' + image_name)
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
        result_urls = []
        try:
            urls_count = len(image_urls)
            for i in range(urls_count):
                new_image = self._local_image_upload(image_urls[i])
                if new_image != '':
                    vk_image = self._vk_image_upload(new_image)
                    if vk_image != {}:
                        result += 'photo{}_{}'.format(vk_image['owner_id'], vk_image['id']) + ('' if i == urls_count - 1 else ',')
                        result_urls.append(vk_image['sizes'][-1]['url'])
            if result != '':
                if result[len(result) - 1] == ',':
                    result[:len(result) - 1:]
            return result, result_urls
        except:
            print_exc()
            return '', []

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
        result_urls = []
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
                result_urls.append(att_photo['sizes'][-1])
            if result != '':
                if result[len(result) - 1] == ',':
                    result = result[:len(result) - 1:]
            return result, result_urls
        except:
            print_exc()
            return '', []
    
    def post_comment(self, topic_name: str, message: str, comment_url='', from_group=1, img_urls=[]) -> tuple:
        """Позволяет создать или изменить комментарий в обсуждении. Для изменения нужно передать ссылку на комментарий

        Args:
            topic_name (str): Название обсуждения
            message (str): Текст комментария
            comment_url (str, optional): url комментария в обсуждении. Передаётся в случае изменения. По умолчанию = ''
            from_group (int, optional): От имени кого будет опубликована запись. 1 - от сообщества, 0 - от имени пользователя. По умолч. = 1
            img_urls (list, optional): Список url картинок, которые необходимо прикрепить. По умолчанию = [].

        Returns:
            tuple: Возвращает url созданного / изменённого комментария + список url прикреплённых к нему изображений
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
            if attachments != ('', []):
                params.setdefault('attachments', attachments[0])
            if comment_url == '':
                comm_id = self.vk.board.createComment(**params)
            else:
                params.pop('guid')
                params.pop('from_group')
                comm_id = int(comment_url[comment_url.find('post=') + 5:])
                if attachments == ('', []):
                    attachments = self._get_previous_attachments(topic_id, comm_id)
                    print('previous_att', attachments)
                    if attachments != ('', []):
                        params.setdefault('attachments', attachments[0])
                params.setdefault('comment_id', comm_id)
                pprint(params)
                if not self.vk.board.editComment(**params):
                    return '', []
        
            res_url = 'https://vk.com/topic-{}_{}?post={}'.format(self.__group_id, topic_id, comm_id)
            return res_url, attachments[1]
        except:
            print_exc()
            return '', []
    
    def _append_unique_user_id(self, comm: dict, admin_ids: set, user_ids) -> list:
        if comm['from_id'] > 0 and comm['from_id'] not in admin_ids:
            new_id = comm['from_id']
            if new_id not in user_ids:
                user_ids.append(new_id)
        return user_ids

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
            user_ids = []
            commentators = []
            last_comment_id = -1
            unique_commentators = []
            while (counter == 1 or len(commentators)):
                params = {
                    'owner_id': -int(self.__group_id),
                    'post_id': post_id,
                    'count': 100,
                    'extended': 1,
                    'sort': 'asc',
                    'fields': 'id,first_name,last_name',
                    'thread_items_count': 10
                }
                if counter > 1:
                    params.setdefault('start_comment_id', last_comment_id)
                    params.setdefault('offset', 1)
                vk_response = self.vk.wall.getComments(**params)
                for profile in vk_response.get('profiles', []):
                    if profile not in unique_commentators:
                        unique_commentators.append(profile)
                comments = vk_response.get('items', [])
                counter += 1
                for comm in comments:
                    user_ids = self._append_unique_user_id(comm, admin_ids, user_ids)
                    thread_comments = comm['thread'].get('items', [])
                    if  thread_comments != []:
                        for t_comm in thread_comments:
                            user_ids = self._append_unique_user_id(t_comm, admin_ids, user_ids)
                if comments != []:
                    last_comment_id = comments[-1]['id']
            result = []
            for user_id in user_ids:
                for profile in unique_commentators:
                    if profile['id'] == user_id:
                        new_tuple = 'https://vk.com/id{}'.format(user_id), str(profile['first_name'] + ' ' + profile['last_name'])
                        result.append(new_tuple)
                        unique_commentators.remove(profile)
            return result, post_url
        except:
            print_exc()
            return [], post_url


    def get_num_id(self, id):
        '''
        Получить имя, фамилию и числовой айди пользователя

        :param id: ссылка на пользователя в произвольном формате
        :return:
        '''

        id = id.split('/')[-1]
        user = self.vk.users.get(user_ids = id, lang = self.lang)
        return ( "{0} {1}".format(user[0]['first_name'], user[0]['last_name']), 'https://vk.com/id{}'.format(user[0]['id']))

    def get_last_lot(self, what_to_find):
        '''
        Возвращает номер последнего лота (коллекта/индивидуалки)
        :param what_to_find: словарь, содержащий имя обсуждения и ключевое слово
        :return:
        '''

        topic_id = self._get_topic_by_name(what_to_find['topic_name'])

        params = {
            'group_id': self.__group_id,
            'topic_id': topic_id,
            'sort': 'desc',
            'count': 100
        }

        comments = self.vk.board.getComments(**params)

        number = 0
        for comment in comments['items']:
            if comment['text'].find(what_to_find['key_word']) == 0:
                number = comment['text'].split('\n')[0].split(' ')[1]
                return number

        return number


    def replace_url(self, topic_name):
        '''
        Заменяет ссылки на пользователей на "тег"

        :param topic_name: Название обсуждения
        :return:
        '''

        topic_id = self._get_topic_by_name(topic_name)

        start_comment_id = 1
        while True:
            params = {
                'group_id': self.__group_id,
                'topic_id': topic_id,
                'sort': 'asc',
                'count': 100,
                'start_comment_id': start_comment_id + 1
            }

            comments = self.vk.board.getComments(**params)
            id = list(comments['items'])[-1]['id']



            if len(comments) <= 1 or id == start_comment_id: break
            start_comment_id = id


            for comment in comments['items']:

                text = comment['text']

                urls = re.findall('- https://(\S+)', text)


                if len(urls) == 0: continue

                print('\n'+text.split('\n')[0])

                for url in urls:
                    user = self.get_num_id(url)
                    print(user)
                    id = re.findall('vk.com/(\S+)', user[1])[0]
                    text = text.replace('https://'+url, '[{0}|{1}]'.format(id, user[0]))

                params_edit = {
                    'group_id': self.__group_id,
                    'topic_id': topic_id,
                    'comment_id': comment['id'],
                    'message': text
                }

                self.vk.board.editComment(**params_edit)
                time.sleep(3)



    def ban_users(self, user_list):
        '''
        Забанить список пользователей
        :param user_list: список словарей с полями 'id' - Ссылка на пользователя; 'comment' - Текст комментария к бану.
        :return:
        '''

        params = {
            'group_id': self.__group_id,
            'comment_visible': 1
        }

        for user in user_list:

            params['owner_id'] = re.findall('id(\d+)',self.get_num_id(user['id'])[1])[0]
            params['comment'] = user['comment']

            self.vk.groups.ban(**params)

    def find_comment(self, what_to_find):
        '''
        Поиск комментария по заданыым критериям
        :param what_to_find: словарь вида { "topic_name" : ..., "type": Коллективка/Индивидуалка/Посылка , "number" : ...}
        :return: возращает инфу о найденном комментарии
        '''

        topic_id = self._get_topic_by_name(what_to_find["topic_name"])

        start_comment_id = 1

        while True:
            params = {
                'group_id': self.__group_id,
                'topic_id': topic_id,
                'sort': 'asc',
                'count': 100,
                'start_comment_id': start_comment_id + 1
            }

            comments = self.vk.board.getComments(**params)
            id = list(comments['items'])[-1]['id']

            if len(comments) <= 1 or id == start_comment_id: break
            start_comment_id = id

            for comment in comments['items']:
                if comment['text'].find(what_to_find['type']) == 0:

                    number = comment['text'].split('\n')[0].split(' ')[1]
                    number = int(re.findall("(\d+)", number)[0])

                    if number == what_to_find["number"]:
                        return comment
                        break


    def edit_comment(self, text, what_to_find):
        '''
        Редактирует определённый комментарий в обсуждении

        :param text: текст, который необходимо вставить
        :param what_to_find: словарь вида { "topic_name" : ..., "type": Коллективка/Индивидуалка/Посылка , "number" : ...}
        :return:
        '''

        comment = self.find_comment(what_to_find)
        old_text = comment['text']

        try:
            start_part = re.search('Состояние: (.+)\n\n', old_text).span()[1]
        except:
            # Состояние: Едет в РФ \n tracks \n\n позиции
            start_part = re.search('\n\n\d', old_text).span()[1] - 1
        end_part = re.search('\n\nПоедет', old_text).span()[0]

        text = old_text[:start_part] + text + old_text[end_part:]

        topic_id = self._get_topic_by_name(what_to_find["topic_name"])
        params_edit = {
            'group_id': self.__group_id,
            'topic_id': topic_id,
            'comment_id': comment['id'],
            'message': text
        }

        self.vk.board.editComment(**params_edit)


    def edit_status_comment(self, what_to_find, status = '', payment = []):
        '''

        :param what_to_find: словарь вида { "topic_name" : ..., "type": Коллективка/Индивидуалка/Посылка , "number" : ...}
        :param status: статус ['Выкупается', 'Едет на склад', 'На складе', 'Едет в РФ', 'На руках', 'Без статуса']. Может быть пустым
        :param payment: список тегов с оплатой. Может быть пустым
        :return:
        '''

        comment = self.find_comment(what_to_find)

        old_text = comment['text']

        text = ''

        # Изменение статуса
        if len(status) > 0:
            status_end_part =  re.search('\n\n\d', old_text).span()[1] - 3
            status_start_part = re.search('Состояние: ', old_text).span()[1]
            text = old_text[:status_start_part] + status + old_text[status_end_part:]

        # Изменение инфы об оплате
        if len(payment) > 0:

            # если статус был уже изменён
            if len(text)>0:
                participants_start_part = re.search('\n\n\d', text).span()[1] - 1
                participants_end_part = re.search('\n\nПоедет', text).span()[0] + 1
            else:
                participants_start_part = re.search('\n\n\d', old_text).span()[1] - 1
                participants_end_part = re.search('\n\nПоедет', old_text).span()[0] + 1
                text = old_text

            text = text[:participants_start_part] + payment + text[participants_end_part:]

        topic_id = self._get_topic_by_name(what_to_find["topic_name"])
        params_edit = {
            'group_id': self.__group_id,
            'topic_id': topic_id,
            'comment_id': comment['id'],
            'message': text
        }

        try:
            self.vk.board.editComment(**params_edit)
        except:
            return -1

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


    def _get_album_by_name(self, album_name: str) -> int:
        """
        Args:
            album_name (str): Название альбома

        Returns:
            int: ID альбома с именем album_name и ID заглавной фотографии альбома или -1
        """

        try:
            # идентификатор сообщества в параметре owner_id необходимо указывать со знаком "-"
            vk_response = self.vk.photos.getAlbums(owner_id = '-'+self.__group_id, need_covers = 1)
            albums = vk_response.get('items', [])
            for album in albums:
                if album['title'] == album_name:
                    return album['id'], album["thumb_id"]
        except:

            return -1, -1


    def delete_photos(self, album_name: str, end_date):


        album_id, cover_id = self._get_album_by_name(album_name)

        # идентификатор сообщества в параметре owner_id необходимо указывать со знаком "-"
        params = { "owner_id": '-' + self.__group_id,
                   "album_id": album_id,
                   "extended": 1,
                   "count": 1000
        }

        photos = self.vk.photos.get(**params)

        params_delete = { "owner_id": '-' + self.__group_id,
        }

        for photo in photos["items"]:
            if cover_id != photo["id"]:
                date = (datetime.fromtimestamp(int(photo["date"]))).date()
                if date < end_date:
                    params_delete["photo_id"] = photo["id"]
                    self.vk.photos.delete(**params_delete)
                else:
                    break




    # ДОДЕЛАТЬ
    def payment_messege(self, mes, user_list):

        params = {
            'message': mes,
            "peer_id": '-'+self.__group_id
        }

        for user in user_list:

            #params['user_id'] = re.findall('id(\d+)',self.get_num_id(user)[1])[0]
            self.vk.messages.send(**params)
