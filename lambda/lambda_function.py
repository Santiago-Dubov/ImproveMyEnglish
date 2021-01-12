# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import random
import logging
import json
import prompts

import requests
import uuid
import time
import sys
import hashlib
import os
import boto3

from ask_sdk_core.skill_builder import CustomSkillBuilder
import ask_sdk_core.utils as ask_utils

#from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_dynamodb.adapter import DynamoDbAdapter
from ask_sdk_dynamodb.adapter import DynamoDbAdapter

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ddb_region = os.environ.get('DYNAMODB_PERSISTENCE_REGION')
ddb_table_name = os.environ.get('DYNAMODB_PERSISTENCE_TABLE_NAME')
ddb_resource = boto3.resource('dynamodb', region_name=ddb_region)
dynamodb_adapter = DynamoDbAdapter(table_name=ddb_table_name, create_table=False, dynamodb_resource=ddb_resource)
sb = CustomSkillBuilder(persistence_adapter=dynamodb_adapter)

TOKEN="Removed Upon Request"
USER="Removed Upon Request"

class PromptQuestionHandler(AbstractRequestHandler):
    """Handler for Skill Launch and PromptQuestion Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("LaunchRequest")(handler_input) or is_intent_name("PromptQuestion")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In PromptQuestionHandler")

        # get localization data
        attr = handler_input.attributes_manager.persistent_attributes

        attr['prompt'] = None
        attr['prompt_given'] = False
            
        handler_input.attributes_manager.session_attributes = attr
        
        speech = "Welcome to the write and improve situational english checking skill. Please choose from one of the following categories: Meeting someone, Eating out, Booking train tickets, The airport."
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response

class RestaurantIntentHandler(AbstractRequestHandler):
    """Handler for RestaurantIntent."""
    
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("RestaurantIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        """Handler for Answer input"""
        logger.info("In RestaurantIntentHandler")
        data = handler_input.attributes_manager.request_attributes["_"]
        attr = handler_input.attributes_manager.session_attributes
        
        random_prompt = random.choice(data[prompts.RESTAURANT_PROMPTS])
        attr['prompt'] = random_prompt
        attr['prompt_given'] = True
        handler_input.attributes_manager.session_attributes = attr
        
        speech = data[prompts.GET_PROMPT_MESSAGE].format(random_prompt)
        
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response

class TrainIntentHandler(AbstractRequestHandler):
    """Handler for TrainIntent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("TrainIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        """Handler for Answer input"""
        logger.info("In TrainIntentHandler")
        attr = handler_input.attributes_manager.session_attributes
        data = handler_input.attributes_manager.request_attributes["_"]
        
        random_prompt = random.choice(data[prompts.TRAIN_PROMPTS])
        attr['prompt'] = random_prompt
        attr['prompt_given'] = True
        handler_input.attributes_manager.session_attributes = attr
        
        speech = data[prompts.GET_PROMPT_MESSAGE].format(random_prompt)
        
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response

class AirportIntentHandler(AbstractRequestHandler):
    """Handler for AirportIntent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AirportIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        """Handler for Answer input"""
        logger.info("In AirportIntentHandler")
        attr = handler_input.attributes_manager.session_attributes
        data = handler_input.attributes_manager.request_attributes["_"]
        
        random_prompt = random.choice(data[prompts.AIRPORT_PROMPTS])
        attr['prompt'] = random_prompt
        attr['prompt_given'] = True
        handler_input.attributes_manager.session_attributes = attr
        
        speech = data[prompts.GET_PROMPT_MESSAGE].format(random_prompt)
        
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response

class MeetingIntentHandler(AbstractRequestHandler):
    """Handler for MeetingIntent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("MeetingIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        """Handler for Answer input"""
        logger.info("In MeetingIntentHandler")
        attr = handler_input.attributes_manager.session_attributes
        data = handler_input.attributes_manager.request_attributes["_"]
        
        random_prompt = random.choice(data[prompts.PROMPTS])
        attr['prompt'] = random_prompt
        attr['prompt_given'] = True
        handler_input.attributes_manager.session_attributes = attr
        
        speech = data[prompts.GET_PROMPT_MESSAGE].format(random_prompt)
        
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response

class GetAnswerHandler(AbstractRequestHandler):
    """Handler for GetAnswerIntent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("GetAnswerIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        """Handler for Answer input"""
        logger.info("In GetAnswerHANDLER")
        user_response = str(handler_input.request_envelope.request.intent.slots["content"].value)
        attr = handler_input.attributes_manager.session_attributes
        #question_text = attr['prompt']
        
        # Making a call to the WI API
        submissionId=str(uuid.uuid1())
        authorId = str(uuid.uuid1())
        question_text =''
        taskId = hashlib.sha224(question_text.encode('utf-8')).hexdigest()[0:40]
        
        r = requests.put("https://api-staging.englishlanguageitutoring.com/v2.1.0/account/%s/text/%s" % (USER,submissionId),
                         headers = {"Authorization": "Token token=%s" % TOKEN},
                         data = {"author_id": authorId,
                                 "task_id": taskId,
                                 "session_id": "1",
                                 "question_text": 1,
                                 "text": user_response,
                                 }
                         ).json()
        if r['type'] != 'success':
            speech = 'An error occured please repeat your answer'
            handler_input.response_builder.speak(speech).ask(speech)
            return handler_input.response_builder.response
        
        r2 = {'type' : 'results_not_ready',
              'estimated_seconds_to_completion' : 2}
        t1 = time.time()
        
        while r2['type'] == 'results_not_ready':
            # As Alexa must return a response within 8 seconds, if the API takes too long we ask them to repeat their answer
            t2 = time.time()
            if t2-t1 > 7.5:
                speech = 'Our servers appear to be busy at the moment, please repeat your answer'
                handler_input.response_builder.speak(speech).ask(speech)
                return handler_input.response_builder.response 
                
            r2 = requests.get("https://api-staging.englishlanguageitutoring.com/v2.1.0/account/%s/text/%s/results" % (USER,submissionId),
                              headers = {"Authorization": "Token token=%s" % TOKEN}).json()

        #Processing of the correction
        logger.info('request: ' + r2['type'])
        speech = 'You answered ' + user_response
        
        ignore_errors = []
        possible_errors = []
        corrections = []
        
        for x in r2['textual_errors']:
            # Ignoring punctuation and spelling errors
            if ('P' in x[3] or x[3] == 'S'):
                ignore_errors.append([x[0],x[1]])
            else:
                corrections.append(x[2])
        
        for token in r2['suspect_tokens']:
            # Record the error if it's not a punctuation or spelling error
            if token not in ignore_errors:
                possible_errors.append(user_response[token[0]:token[1]])

        if len(possible_errors) >= 1:
            speech = speech + '. We believe there may be errors in the words:, ' + ' ,'.join(possible_errors)
            if len(corrections) > 0:
                speech = speech + '. We suggest these alternatives:, ' + ' ,'.join(corrections)
        else:
            speech = speech + '. We did not detect any errors'
        speech = speech + '... Please choose a new category'
        
        # Confirming 
        attr['prompt_given'] = False
        handler_input.attributes_manager.session_attributes = attr
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response
        
    

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response

class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for Fallback Intent.

    AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input): 
        # get localization data
        
        data = handler_input.attributes_manager.request_attributes["_"]
        attr = handler_input.attributes_manager.session_attributes
        
        if attr['prompt_given']:
            speech = "Your answer may be too long or you may have forgotten to start your answer with the word, 'answer'"
            reprompt = speech
            
        else:   
            speech = data[prompts.FALLBACK_MESSAGE]
            reprompt = data[prompts.FALLBACK_REPROMPT]
            
        handler_input.response_builder.speak(speech).ask(
            reprompt)
        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )



class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Your answer may be too long. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class LocalizationInterceptor(AbstractRequestInterceptor):
    """
    Add function to request attributes, that can load locale specific data.
    """

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale))

        # localized strings stored in language_strings.json
        with open("language_strings.json") as language_prompts:
            language_data = json.load(language_prompts)
        # set default translation data to broader translation
        if locale[:2] in language_data:
            data = language_data[locale[:2]]
            # if a more specialized translation exists, then select it instead
            # example: "fr-CA" will pick "fr" translations first, but if "fr-CA" translation exists,
            # then pick that instead
            if locale in language_data:
                data.update(language_data[locale])
        else:
            data = language_data[locale]
        handler_input.attributes_manager.request_attributes["_"] = data



# Request and Response loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""

    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""

    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))
        
# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


#sb = SkillBuilder()
sb = CustomSkillBuilder(persistence_adapter=dynamodb_adapter)
sb.add_request_handler(PromptQuestionHandler())
sb.add_request_handler(RestaurantIntentHandler())
sb.add_request_handler(TrainIntentHandler())
sb.add_request_handler(AirportIntentHandler())
sb.add_request_handler(MeetingIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(GetAnswerHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers


# Register request and response interceptors
sb.add_global_request_interceptor(LocalizationInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())



lambda_handler = sb.lambda_handler()