import json

from django.http.response import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

import fb_bot.messenger_manager as messenger_manager
import highlights.settings
from fb_bot import user_manager
from fb_bot.logger import logger


class DebugPageView(TemplateView):
    template_name = "debug.html"


class HighlightsBotView(generic.View):
    LATEST_SENDER_ID = 0

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        if request.GET['hub.verify_token'] == 'ea30725c72d35':
            return HttpResponse(request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        logger.log("Message received: " + str(request.body))

        # Converts the text payload into a python dictionary
        incoming_message = json.loads(request.body.decode('utf-8'))

        response_msg = ""

        for entry in incoming_message['entry']:

            for message in entry['messaging']:

                HighlightsBotView.LATEST_SENDER_ID = message['sender']['id']
                user = user_manager.get_user(HighlightsBotView.LATEST_SENDER_ID)

                logger.log_for_user("Message received: " + str(message), HighlightsBotView.LATEST_SENDER_ID)

                # Events
                if 'message' in message:
                    response_msg = messenger_manager.send_highlight_message_for_team(HighlightsBotView.LATEST_SENDER_ID,
                                                                                     message['message']['text'])

                elif 'postback' in message:
                    postback = message['postback']['payload']

                    if postback == 'get_started':
                        response_msg = messenger_manager.send_facebook_message(HighlightsBotView.LATEST_SENDER_ID,
                                       messenger_manager.create_message("Hi Boss! I am the smart bot that fetches the "
                                       "latest football highlights for you :) To get started, enter the name of any team you love to see the highlights for!"))

                    elif postback == 'recent':
                        response_msg = messenger_manager.send_highlight_message_recent(HighlightsBotView.LATEST_SENDER_ID)

                    elif postback == 'popular':
                        response_msg = messenger_manager.send_highlight_message_popular(HighlightsBotView.LATEST_SENDER_ID)

                logger.log_for_user("Message sent: " + str(response_msg), HighlightsBotView.LATEST_SENDER_ID)
                HighlightsBotView.LATEST_SENDER_ID = 0

        # For DEBUG MODE only
        if highlights.settings.DEBUG:
            return JsonResponse(response_msg, safe=False)

        return HttpResponse()
