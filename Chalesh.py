import kivy
from telegram.ext import Updater, CommandHandler, Filters, MessageHandler,CallbackQueryHandler
import os
import datetime

import bidi.algorithm
import arabic_reshaper

from pymongo import MongoClient
from telegram import ReplyKeyboardMarkup,InlineKeyboardButton , InlineKeyboardMarkup
import dotenv
import sys

#try:
from kivy.app import App
#except ImportError:
#    import pip._internal as pip
#    pip.main(['install', 'kivy'])




from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown

from kivy.uix.screenmanager import ScreenManager, ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.uix.treeview import TreeViewLabel ,TreeViewLabel




class WindowManager(ScreenManager):
    pass

class MainScreen(FloatLayout):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)

class ChaleshApp(App):
    def build(self):
        self.bot = Chalesh()
        layout = FloatLayout()
        values = cleaning.find_one({"_id": chaleshID})['settings']
        # configure spinner object and add to layout
        self.spinnerObject = Spinner(text="Message Type", values=values)
        self.spinnerObject.size_hint = (0.3, 0.1)
        self.spinnerObject.pos_hint = {'x': .05, 'y': .8}
        layout.add_widget(self.spinnerObject)
        self.spinnerObject.bind(text=self.on_spinner_select)
        self.spinnerSelection = Label(text="%s" % self.spinnerObject.text)
        layout.add_widget(self.spinnerSelection)

        types = {'Count', 'Duration'}
        dropdown = DropDown()
        for index in types:
            btn = Button(text='%s' % index, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: dropdown.select(btn.text))
            dropdown.add_widget(btn)

        self.mainbutton = Button(text='Run', size_hint=(.2, .1))
        self.mainbutton.pos_hint = {'x': 0.4, 'top': .9}
        self.mainbutton.bind(on_release=dropdown.open)
        dropdown.bind(on_select=lambda instance, x: setattr(self.mainbutton, 'text', x))
        layout.add_widget(self.mainbutton)

        self.periodtxt = TextInput()
        self.periodtxt.multiline = False
        self.periodtxt.pos_hint = {'x': 0.65, 'top': .9, 'height': .1}
        self.periodtxt.size_hint = (.1, .1)
        layout.add_widget(self.periodtxt)

        self.infotxt = TextInput()
        self.infotxt.multiline = True
        self.infotxt.pos_hint = {'x': 0.05, 'top': .75, 'height': .5}
        self.infotxt.size_hint = (.6, .5)
        self.infotxt.background_color = (0, 0, 1, 1)
        fontspath = os.environ['WINDIR'] + "\\Fonts\\"
        self.infotxt.font_name = fontspath + "\\arial"
        self.infotxt.font_size = 20
        self.infotxt.base_direction = "rtl"
        text_width = self.infotxt._get_text_width(
            self.infotxt.text,
            self.infotxt.tab_width,
            self.infotxt._label_cached
        )
        self.infotxt.padding_x = (self.infotxt.width - text_width) / 2
        layout.add_widget(self.infotxt)

        # self.tv = TreeViewLabel()
        # for val in values:
        #     self.tv.add_node(TreeViewLabel(text=val))
        #
        # self.tv.size_hint = (.5, .1)
        # self.tv.pos_hint = {'x': .65, 'top': .75}
        # layout.add_widget(self.tv)
        # add a label displaying the selection from the spinner
        # self.spinnerObject.text

        self.savebtn = Button(text="Save")
        self.savebtn.size_hint = (.15, .1)
        self.savebtn.pos_hint = {'x': .8, 'y': 0.8}
        layout.add_widget(self.savebtn)

        self.runbtn = Button(text="Start")
        self.runbtn.size_hint = (.15, .1)
        self.runbtn.pos_hint = {'x': .2, 'y': 0.1}
        layout.add_widget(self.runbtn)
        self.runbtn.bind(on_press=self.runBot)
        return layout

    def runBot(self, instance):
        if self.runbtn.text == 'Start':
            self.runbtn.text = 'Stop'
            self.bot.chaleshBot()
        else:
            self.runbtn.text = 'Start'
            self.bot.stopUpdater()
        return

        # call back for the selection in spinner object

    def on_spinner_select(self, spinner, text):
        self.spinnerSelection.text = "Selected value in spinner is: %s" % self.spinnerObject.text
        # print('The spinner', spinner, 'have text', text)


class Chalesh():
    def __init__(self):
        self.percentDeleteOnStep = 0.01
        self.chaleshID = chaleshID
        return

    def stopUpdater(self):
        self.updater.stop()
        return


    def startUpdater(self):
        self.updater.idle()
        return

    def start(self,bot,update):
        bot.send_message(text="سلام آماده ام" , chat_id=update.message.chat_id, reply_markup=self.inlineKey)
        return

    def queryByDuration(self,type):
        deleteCandidates={}
        period=cleaning.find({"_id": self.chaleshID },{"settings."+type+".number"})[0]['settings'][type]['number']
        completedDate = cleaning.find({"_id":self.chaleshID},{"completed"})[0]["completed"]
        startTime = cleaning.find({"_id":self.chaleshID},{"start"})[0]["start"].time()

        try:
            critical_date=datetime.datetime.today()-datetime.timedelta(days=period)
            if completedDate < datetime.datetime.today() and datetime.datetime.now().time() > startTime:
                deleteCandidates=collection.find({"chat_id": self.chaleshID,"date": { "$lte": critical_date }})
                completedDate=datetime.datetime.today()
                try:
                    #print("")
                    cleaning.update_one({"_id": self.chaleshID}, { "$set": { "completed": datetime.datetime.today() } })
                except Exception as exp:
                    #print("Error:", exp)
                    pass
        except Exception as exp:
            #print("Error Cleaning",exp)
            pass
        return deleteCandidates

    def registerIt(self,message_id,chat_id,user_id,type="Unknown",info=""):
        if chat_id!= self.chaleshID:
            return
        #print("message_id:", message_id, " chat_id:", chat_id, " user_id:", user_id, " Type:", type)
        #info= "message_id:" + str(message_id) + " chat_id:"+ str(chat_id) + " user_id:"+ str(user_id) + " Type:" + type
        #print(info)
        challenge.infotxt.foreground_color = (1, 1, 0, 1)
        challenge.infotxt.text +=  str(info['id']) + "\n" + bidi.algorithm.get_display(arabic_reshaper.reshape(info['first_name'])) + "\n" + str(datetime.datetime.now().strftime('%d, %b %Y - %H:%M'))+'\n' *3

        message = {"_id": message_id,
                   "chat_id": chat_id,
                   "user_id": user_id,
                   "date": datetime.datetime.today(),
                   "type": type}  # ,"type": type

        try:
            collection.insert_one(message)
        except Exception as exp:
            #print("Error register:", exp)
            pass
        return

    def queryByCount(self,type):
        #,message_id,chat_id,user_id,type="Unknown"
        removeIdsArray={}

        maxMessages= cleaning.find({"_id": self.chaleshID },{"settings."+type+".number"})[0]['settings'][type]['number']
        mindel=int(maxMessages * self.percentDeleteOnStep)
        countOfType = collection.count_documents({"chat_id": self.chaleshID , "type":type})
        try:
            challenge.infotxt.foreground_color = (0, 1, 0, 1)
            challenge.infotxt.text += "Count of " + type + ": " + str(countOfType) + '\n'
            #print("Count: ", countOfType)
            delNumber = countOfType - maxMessages
            if min(mindel,delNumber)>0:
                removeIdsArray = collection.find({"chat_id":self.chaleshID}, {"_id": 1}).sort([("date", 1)]).limit(min(mindel,delNumber))   #.map(function(doc) {return doc._id;}); # Pull out just the _ids
        except Exception as e:
            #print ("Error limit 1000: ", e)
            pass


        ########################################
        # #print(message)
        return removeIdsArray

    def registerID(self,bot,update):
        #print(update.message.from_user)
        removeIdsArray = {}
        removeIdsArray = self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'],
                      info=update.message.from_user)

        ################################ Cleaning  ################
        return


    def removeMessageLeft(self,bot,update):
        #print ("Start removeMessageLeft")
        bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
        #print(update.message.message_id , " removed")
        return

    def callback_func(self, bot, update):
        # print("-"*40)
        # print("new_chat_members","\nupdate._effective_message",update._effective_message,"\nupdate.update_id",update.update_id,
        #       "\nupdate.message.message_id", update.message.message_id,"\nupdate.message.text",update.message.text)
        # # here you receive a list of new members (User Objects) in a single service message
        # new_members = update.message.new_chat_membersp
        #print("Effective message:",update._effective_message)
        #print ("Start callback_func Joinning Message")
        bot.delete_message(chat_id=update._effective_message.chat_id, message_id=update._effective_message.message_id)
        #print(update._effective_message.message_id, " removed")
        # do your stuff here:
        # for member in new_members:
        #     print(member.username)
        return


    def setTime(self,bot,update):
        bot.send_message("زمان شروع عملیات پاکسازی را مطابق با قالب ساعت : دقیقه وارد کنید", chat_id=update.message.chat_id, reply_markup=self.key)
        self.operation="setTime"
        return

    def setPeriod(self,bot,update):
        # bot.send_message("پیامهای مربوط به چند روز قبل حذف شوند؟",chat_id = update.message.chat_id , reply_markup=self.key)
        # self.operation="setPeriod"
        return

    # def buttonsDriven(self,bot,update):
    #     button = update.callback_query
    #     if button=='time':
    #         # if self.operation=="setTime":
    #         bot.send_message("زمان شروع را وارد کنید",chat_id=update.message.chat_id, reply_markup=self.inlineSaveTimeKey)
    #     if button=='save time':
    #         startText=update.message.text
    #         defaultTime=datetime.datetime.strptime("16:30","%h:%m")
    #         try:
    #             self.startTime=datetime.datetime.strftime(startText,"%h:%m")
    #         except:
    #             self.startTime=defaultTime
    #             #print("زمان شروع پاکسازی صحیح نمیباشد برای مثال طبق قالب ? ده دقیقه بعد از نیمه شب وارد کنید", self.startTime)
    #         #self.clean["start"]=self.startTime
    #     if button=='duration':
    #         bot.send_message("زمان شروع را وارد کنید", chat_id=update.message.chat_id,
    #                          reply_markup=self.inLineSaveDurationKey)
    #     #if button=='save duration':
    #         #if button == 'save time':
    #         # if self.operation == "setPeriod":
    #
    #                 #print("عددد وارد شده معتبر نمیباشد لطفأ دومرتبه سعی کنید")
    #     return

    def registerVideo(self,bot,update):
        type="Video"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)

        removeIdsArray={}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    #print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id":self.chaleshID,"_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    #print("Removed: ", id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print (e)

        return

    def registerText(self,bot,update):
        type = "Text"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'],type,
                      info=update.message.from_user)

        removeIdsArray = {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    #print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))

                    collection.delete_one({"chat_id":self.chaleshID,"_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    #challenge.infotxt.foreground_color=(1,0,0,1)
                    # challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                    challenge.infotxt.foreground_color = (1, 0, 0, 1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) + '\n'

                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print (e)

        return

    def registerReplay(self,bot,update):
        type="Replay"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)

        removeIdsArray = {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    # print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id": self.chaleshID, "_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print(e)
        return

    def registerAnimation(self,bot,update):
        type="Animation"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)

        removeIdsArray = {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    #print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id":self.chaleshID,"_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print (e)

        return

    def registerCommand(self,bot,update):
        type="Command"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)

        removeIdsArray= {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    # print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id": self.chaleshID, "_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print(e)
        return

    def registerContact(self, bot,update):
        type="Contact"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)
        removeIdsArray= {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)


        try:
            for id in removeIdsArray:
                try:
                    # print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id": self.chaleshID, "_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print(e)

        return

    def registerDocument(self,bot,update):
        type = "Document"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type=type,
                      info=update.message.from_user)
        removeIdsArray = {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    # print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id": self.chaleshID, "_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print(e)
        return

    def registerForwarded(self,bot,update):
        type="Forwarded"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)
        removeIdsArray = {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    # print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id": self.chaleshID, "_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print(e)
        return

    def registerGame(self,bot,update):
        type="Game"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)
        removeIdsArray = {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    # print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id": self.chaleshID, "_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print(e)
        return

    def registerGroup(self,bot,update):
        type="Group"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)
        removeIdsArray = {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    # print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id": self.chaleshID, "_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    print("Removed: ", self.chaleshID)
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print(e)
        return

    def registerInvoice(self,bot,update):
        type="Invoice"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)
        removeIdsArray = {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    # print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id": self.chaleshID, "_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print(e)
        return

    def registerLocation(self,bot,update):
        type="Location"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)
        removeIdsArray = {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    # print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id": self.chaleshID, "_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print(e)
        return

    def registerPassport_data(self,bot,update):
        type="Passport"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)
        removeIdsArray = {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    # print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id": self.chaleshID, "_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print(e)
        return

    def registerPhoto(self,bot,update):
        type="Photo"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)
        removeIdsArray = {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    # print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id": self.chaleshID, "_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print(e)

        return

    def registerPrivate(self,bot,update):
        type="Private"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)
        removeIdsArray = {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    # print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id": self.chaleshID, "_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print(e)

        return



    def registerSticker(self,bot,update):
        type="Sticker"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)
        removeIdsArray = {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    # print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id": self.chaleshID, "_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print(e)

        return

    def registerVenue(self,bot,update):
        type = "Venue"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)
        removeIdsArray = {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    # print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id": self.chaleshID, "_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print(e)

        return

    def registerVideo_Note(self,bot,update):
        type = "Video_Note"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)
        removeIdsArray = {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    # print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id": self.chaleshID, "_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print(e)

        return

    def registerVoice(self,bot,update):
        type="Voice"
        self.registerIt(update.message.message_id,
                      update.message.chat_id,
                      update.message.from_user['id'], type,
                      info=update.message.from_user)
        removeIdsArray = {}
        rmv_type = cleaning.find({"_id": self.chaleshID}, {"settings." + type + ".rmv_type"})[0]['settings'][type][
            'rmv_type']

        if rmv_type == "Daily":
            removeIdsArray = self.queryByDuration(type=type)
        elif rmv_type == "Count":
            removeIdsArray = self.queryByCount(type=type)

        try:
            for id in removeIdsArray:
                try:
                    # print("ready to delete: chat_id={}, message_id={}".format(self.chaleshID,id["_id"]))
                    collection.delete_one({"chat_id": self.chaleshID, "_id": id["_id"]})
                    bot.delete_message(chat_id=self.chaleshID, message_id=id["_id"])
                    challenge.infotxt.foreground_color=(1,0,0,1)
                    challenge.infotxt.text += "Removed: ", str(id["_id"]) +'\n'
                except Exception as e:
                    #print(e)
                    continue
        except Exception as e:
            pass
            #print(e)

        return

    def chaleshBot(self):
        self.updater=Updater("349821902:AAFDHs18HQLUzDNWSvpun8kolbQuvZAoQlE")
        self.updater.dispatcher.add_handler(CommandHandler("start", self.start))
        #updater.dispatcher.add_handler(CommandHandler("time", self.setTime))
        #updater.dispatcher.add_handler(CommandHandler("period", self.setPeriod))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.status_update.left_chat_member,self.removeMessageLeft))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.status_update.new_chat_members, self.callback_func))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.video,self.registerVideo))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.text,self.registerText))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.animation,self.registerAnimation))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.command,self.registerCommand))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.contact,self.registerContact))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.document,self.registerDocument))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.forwarded,self.registerForwarded))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.game,self.registerGame))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.group,self.registerGroup))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.invoice,self.registerInvoice))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.location,self.registerLocation))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.passport_data,self.registerPassport_data))
        #Video,Text,Animation,Command,Contact,Document,Forwarded,Game,Group,Invoice,Location,Passport_data
        #Photo,Private,Replay,Sticker,Venue,Video_Note,Voice
        self.updater.dispatcher.add_handler(MessageHandler(Filters.photo,self.registerPhoto))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.private,self.registerPrivate))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.reply,self.registerReplay))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.sticker,self.registerSticker))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.venue,self.registerVenue))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.video_note,self.registerVideo_Note))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.voice,self.registerVoice))
        self.updater.dispatcher.add_handler(MessageHandler(Filters.all,self.registerID))
        #updater.dispatcher.add_handler(CallbackQueryHandler(self.buttonsDriven))
        #updater.dispatcher.add_handler(MessageHandler(Filters.status_update,self.test_filters_status_update))
        self.updater.start_polling()

        return


if __name__=="__main__":
    #print(sys.version)
    #kivy.require('1.11.1')
    dotenv.load_dotenv()
    user = os.getenv('user')
    password = os.getenv('password')
    # cleaning.update_many( { "_id" : self.chaleshID }, { "$pull" : { "settings" }})
    cluster = MongoClient(
        f"mongodb+srv://{user}:{password}@cluster0-j47c5.gcp.mongodb.net/test?retryWrites=true&w=majority")
    # print(cluster)
    db = cluster["Chalesh"]
    collection = db["Messages"]
    cleaning = db["Cleaning"]
    chaleshID = int(os.getenv('chaleshID'))
    if cleaning.find_one({})["_id"] != chaleshID:
        sys.exit()
    challenge = ChaleshApp()
    challenge.run()


