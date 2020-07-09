
r'''

  ______          ____        _
 |  ____|        |  _ \      | |
 | |__ _   _ _ __| |_) | ___ | |_
 |  __| | | | '__|  _ < / _ \| __|
 | |  | |_| | |_ | |_) | (_) | |_
 |_|   \__,_|_(_)|____/ \___/ \__|

public Vkontakte Bot FurBot
 *author: FluffyMak4ik
 *rework: Foxsome
 *last-version: 1.0r2
 ` FurBot is a bot written for
   the VKontakte social network
   in order to pump out pictures
   from the e926.net website

public module main.py of FurBot
 ` ...

'''

import os
import io
import re  # RegEx support was added in 1.0
import abc  # Abstraction was added in 1.0 Revision 2 (1.0r2)
import json  # JSON support was added in 1.0
import enums  # Enumerators were added in 1.0 Revision 2 (1.0r2)
import random  # Randomizing is avaible now!
import aiohttp  # Asynchronous HTTP support was added in 1.0r2
import asyncio  # Asyncio support was added in 1.0r2
import traceback  # Neccessary to get out errors

import vk_api as vkontakte

from vk_api import (
    VkUpload
)
from cached_property import (
    cached_property as cproperty
)
from vk_api.utils import (
    get_random_id as getRandomId
)
from vk_api.longpoll import (
    VkLongPoll,
    VkEventType
)


'''
======================================================================

section <Base Bot Engine>

'''


class RegEx(enums.Enum):
    '''

    private const WRD
     ` RegEx pattern to parse
       command words. When prefix
       is * and received
       text is *help, you will get
       command word "help".

    '''
    WRD = r'^%s([^" ]*)'

    '''

    private const ARG
     ` RegEx pattern to parse
       arguments in command.

    '''
    ARG = r'["]([^"]*)["]|\s+([^" ]+)'


class Format(enums.Enum):
    '''

    public const ATC
     ` ...

    '''
    ATC = "%s%s_%s"


class Parser(object):
    '''

    private class Parser of module main.py of FurBot
     *author: Foxsome
     ` ...

    private class Parser
     ` ...

    '''

    def __init__(self, prefix, string):
        self._prefix = prefix
        self._string = string

    def _parseWord(self, prefix, string):
        parsed = re.findall(RegEx.WRD % prefix, string)
        if parsed:
            return parsed[0]

    def _parseArguments(self, string):
        return [
            quote or dquote for quote, dquote in re.findall(
                RegEx.ARG, string)
        ]

    @property
    def prefix(self):
        '''

        public property prefix
         ` Normalizing command prefix

        '''
        return re.escape(self._prefix)

    @property
    def string(self):
        return self._string

    @property
    def word(self):
        return self._parseWord(self.prefix, self.string)

    @property
    def args(self):
        return self._parseArguments(self.string)


class Attachment(object):

    def __init__(self, type, owner, id):
        self.type = type
        self.owner = owner
        self.id = id

    def format(self):
        return Format.ATC % (
            self.type,
            self.owner,
            self.id
        )


class Bot(vkontakte.VkApi):

    '''

    public class Bot
     *implements: VkApi
     ` ...

    '''

    commands = {}

    def __init__(self, prefix, **kwargs):
        super(Bot, self).__init__(**kwargs)

        self.prefix = prefix

    @cproperty
    def api(self):
        '''

        public cached-property api
         ` ...

        '''
        return self.get_api()

    @cproperty
    def longpoll(self):
        '''

        public cached-property longpoll
         ` ...

        '''
        return VkLongPoll(self)

    @cproperty
    def eventloop(self):
        '''

        public cached-property eventloop
         ` ...

        '''
        return asyncio.get_event_loop()

    async def _invokeCommand(self, event, word, args):
        '''

        private coroutine invokeCommand
         ` ...

        '''
        await self.commands[word](self, event, *args)

    async def _handleCommand(self, event, text):
        '''

        private coroutine handleCommand
         ` ...

        '''
        parsed = Parser(self.prefix, text)
        if parsed.word:
            await self._invokeCommand(
                event,
                parsed.word,
                parsed.args
            )

    async def _longpollLoop(self, longpoll):
        '''

        private coroutine longpollLoop
         ` ...

        '''
        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                try:
                    await self._handleCommand(event, event.text)
                except Exception as exc:
                    print(traceback.format_exc())

    def run(self):
        '''

        public method run
         ` ...

        '''
        self.eventloop.run_until_complete(
            self._longpollLoop(self.longpoll)
        )

    def addCommand(self, name, coro):
        self.commands[name] = coro

    def removeCommand(self, name):
        del self.commands[name]


'''
======================================================================

section <FurBot>

'''


class Meta(enums.Enum):
    '''

    public const VKT
     ` Vkontakte bot token is empty string
       by default, as FurBot token remains
       secret.

    '''
    VKT = os.environ.get('VK_API_TOKEN')

    '''

    public const USR
     ` Represent user agent name

    '''
    USR = "VkFurBot0.1"

    '''

    public const HDR
     ` Changing user agent name

    '''
    HDR = {
        'User-Agent': USR
    }

    '''

    public const PRF
     ` Changing user agent name

    '''
    PRF = '.'


class Urls(enums.Enum):
    '''

    public const BAS
     ` Base e926 link (https://e926.net)

    '''
    BAS = "https://e926.net/"

    '''

    public const JSN
     ` ...

    '''
    JSN = BAS + "posts.json?page=%s&tags=%s"


class Ratings(enums.Enum):
    '''

    public const SAV
     ` Some of images on e926
       has rating and by
       default this rating is
       "s"

    '''
    SAV = "s"


class ABCData(metaclass=abc.ABCMeta):

    '''

    abstract class ABCMeta
     ` Represents all of data containers

    '''

    def __init__(self, data):
        self.data = data


class Image(ABCData):

    '''

    public class Image
     * implements: ABCData
     ` ...

    '''
    pass


class PostData(ABCData):

    @property
    def id(self):
        '''

        public async property general
         ` ...

        '''
        return str(self.data['id'])

    @property
    def file(self):
        '''

        public async property file
         ` ...

        '''
        return self.data['file']

    @property
    def rating(self):
        '''

        public async property general
         ` ...

        '''
        return self.data['rating']

    @property
    def imageUrl(self):
        '''

        public async property imageUrl
         ` ...

        '''
        return self.file['url']


class PageData(ABCData):

    '''

    public class PageData
     * implements: ABCData
     ` ...

    '''

    @property
    def dict(self):
        '''

        public async property dict
         ` ...

        '''
        return json.loads(self.data)

    @property
    def posts(self):
        return self.dict['posts']

    def getRandomPost(self):
        return PostData(
            random.choice(self.posts)
        )

    def getRandomPosts(self, limit):
        return random.choices(self.posts, k=limit)


class Downloader(object):

    async def downloadImage(self, session, url):
        async with session.get(url) as response:
            return Image(
                await response.read()
            )

    async def downloadPageData(self, session, url):
        async with session.get(url) as response:
            return PageData(
                await response.text()
            )


class FurBot(Bot):

    def __init__(self, *args, **kwargs):
        super(FurBot, self).__init__(*args, **kwargs)

        self.addCommand('rand', self.randomize)
        self.addCommand('ранд', self.randomize)

    @cproperty
    def uploader(self):
        '''

        public cached-property uploader
         ` ...

        '''
        return VkUpload(self)

    @cproperty
    def downloader(self):
        '''

        public cached-property downloader
         ` ...

        '''
        return Downloader()

    '''
    ------------------------------------------------------------------

    section <Image Randomizer> of class FurBot
     * author: Foxsome
     ` ...

    '''

    async def _getImage(self, session, postData):
        return await self.downloader.downloadImage(
            session,
            postData.imageUrl
        )

    async def _getPageData(self, session, page, category):
        return await self.downloader.downloadPageData(
            session,
            await self._prepareImageUrl(
                page,
                category
            )
        )

    async def _getRandomPost(self, pageData):
        return pageData.getRandomPost()

    async def _prepareImageUrl(self, page, category):
        return Urls.JSN % (
            page,
            category
        )

    async def _photoToAttachment(self, photoData):
        return Attachment(
            'photo',
            photoData.get('owner_id'),
            photoData.get('id')
        )

    async def randomize(self, bot, event, page, category):
        '''

        public coroutine randomize(bot, event, page, category)
         ` ...

        '''
        api = self.api

        async with aiohttp.ClientSession(headers=Meta.HDR) as sess:

            postData = await self._getPageData(
                sess,
                page,
                category
            )

            randomPost = await self._getRandomPost(
                postData
            )

            image = await self._getImage(
                sess,
                randomPost
            )

            attachment = await self._photoToAttachment(
                self.uploader.photo_messages(
                    photos=io.BytesIO(image.data)
                )[0]
            )
            api.messages.send(
                user_id=event.user_id,
                message="🆔 : %s" % randomPost.id,
                attachment=attachment.format(),
                random_id=getRandomId()
            )


if __name__ == '__main__':
    bot = FurBot(
        prefix=Meta.PRF,
        token=Meta.VKT
    )

    bot.run()
