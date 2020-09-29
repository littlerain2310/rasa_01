from typing import Any, Text, Dict, List
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from rasa_sdk.events import SlotSet,Form,ReminderScheduled,ActionReverted,UserUtteranceReverted,FollowupAction,AllSlotsReset
from rasa.core.slots import Slot
import datetime
import time
from threading import Timer
import re


class BeginForm(FormAction):
    def name(self):
        return "begin_form"
    @staticmethod
    def required_slots(tracker)-> List[Text]:
        if tracker.get_slot("contents")=="Khác":
            return ["contents"]
        else:
            return ["contents","services"]
    @staticmethod
    def contents_db() -> List[Text]:
        '''database of contents'''
        return [
            "tư vấn sản phẩm dịch vụ",
            "tư vấn việc làm",
            "khác",
        ]
    @staticmethod
    def services_db() -> List[Text]:
        '''database of services'''
        return [
            "phần mềm contact center",
            "dịch vụ telesales",
            "dịch vụ chăm sóc khách hàng",
            "dịch vụ mystery shopping",
            "dịch vụ tuyển dụng",
            "dịch vụ đào tạo",
            "dịch vụ nhập liệu",
            "dịch vụ field-work",
        ]
    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        )  ->List[Dict]:
        if tracker.get_slot("contents")=="Khác":
            dispatcher.utter_message("Vui lòng liên hệ với agent")
            return []
        else:
            return []
    def slot_mappings(self) :
        return { 
            "contents": [self.from_entity(entity="contents",not_intent="chitchat"),
                        self.from_text()
            ],
            "services": [self.from_entity(entity="services",not_intent="chitchat"),
                        self.from_text()
                        ]
        }
    def validate_contents(self,value: Text, dispatcher, tracker, domain) ->List[Text]:
        if value.lower() in self.contents_db():
            if value.lower() == 'khác':
                buttons = []
                buttons.append(
                    {"title":"tư vấn sản phẩm dịch vụ","payload":"tư vấn sản phẩm dịch vụ"}
                    )
                buttons.append(
                    {"title":"tư vấn việc làm","payload":"tư vấn việc làm"}
                    )
                message='Xin lỗi quý khách,hiện tại hệ thống của chúng em mới bao gồm 2 dịch vụ là :\n1.Tư vấn sản phẩm dịch vụ\n2.tư vấn việc làm\nMong quý khách thông cảm và vui lòng chọn lại'
                dispatcher.utter_button_message(message,buttons)
                return {"contents": None}
            else:
                return {"contents": value}
        else:
            return {"contents": None}
    def validate_services (self,value: Text, dispatcher, tracker, domain) ->List[Text]:
        if value.lower() in self.services_db():
            return {"services": value}
        else:
            return {"services": None}

class MiddleForm(FormAction):
    def name(self):
        return "middle_form"
    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        )  ->List[Dict]:
        
        return []
    @staticmethod
    def required_slots(tracker) -> List[Text]:
        if tracker.get_slot("choices")=='Nhận tư vấn ngay':
            if tracker.get_slot("services") == 'Dịch vụ đào tạo' :
                return ["choices","trainning_package"]
            else: 
                return ["choices","demand"]
        else:
            return ["choices","docs"]
    
    def slot_mappings(self) :
        return { 
            "demand": [
                self.from_text()
            ],
            "choices": [
                self.from_entity(entity="choices",not_intent="chichat"),
                self.from_text()
            ],
            "trainning_package": [
                self.from_entity(entity="trainning_package",not_intent="chichat"),
                self.from_text()
            ],
            "docs": [
                self.from_entity(entity="docs",not_intent="chichat"),
                self.from_text()
            ]
        }

    @staticmethod
    def choices_db() -> List[Text]:
        return [
            "nhận tư vấn ngay",
            "xem tài liệu"
        ]
    
    @staticmethod
    def trainning_package_db() -> List[Text]:
        return [
            "đào tạo dịch vụ khách hàng",
            "đào tạo kỹ năng outbound",
            "đào tạo quản trị và điều hành contact center",
            "đào tạo trải nghiệm khách hàng trong thời đại số",
            "đào tạo nâng cao năng lực quản lý cấp trung"
        ]
    
    @staticmethod
    def docs_db() -> List[Text]:
        return [
            "tìm hiểu về dịch vụ",
            "xem case study",
            "báo giá"
        ]
    
    def validate_choices (self,value: Text, dispatcher, tracker, domain) ->List[Text]:
        if value.lower() in self.choices_db():
            return {"choices": value}
        else:
            return {"choices": None}

    def validate_trainning_package (self,value: Text, dispatcher, tracker, domain) ->List[Text]:
        if value.lower() in self.trainning_package_db():
            return {"trainning_package": value}
        else:
            return {"trainning_package": None}

    def validate_docs (self,value: Text, dispatcher, tracker, domain) ->List[Text]:
        if value.lower() in self.docs_db():
            return {"docs": value}
        else:
            return {"docs": None}

class EndForm(FormAction):
    def name(self) -> Text:
        return "end_form"
    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
        )  ->List[Dict]:
        if tracker.get_slot("additional_support")=="không":
            dispatcher.utter_message("Dạ, vậy em xin đóng phiên chat tại đây. Cảm ơn quý khách đã liên hệ đến BHS, nếu có thêm thông tin nào cần hỗ trợ thêm, quý khách đừng ngại chat vào đây hoặc gọi đến hotline 1900 1739 để được tư vấn nhé. Chúc quý khách một ngày tuyệt vời!")
            return []
        if tracker.get_slot("call") == "chat trực tiếp với tổng đài viên":
            dispatcher.utter_message("Chuyển đến admin trực webchat")
            return []
        else:
            dispatcher.utter_message("Chuyển đến admin webchat")
            return []
    @staticmethod
    def is_phone(string: Text) -> bool:
        """Check if a string is an integer."""
        try:
            value = int(string)
            regex = "\w{10}"
            if re.search(regex,string):
                return True
        except :
            return False
    @staticmethod
    def convert_tail(s):
        s=s.lower()
        if "h" in s:
            s=s.replace("h","")
            print("1")
            return s
        else:
            print("2")
            return s
    @staticmethod
    def required_slots(tracker) -> List[Text]:
        if tracker.get_slot("call") == "Chat trực tiếp với tổng đài viên":
            return["call"]
        return [
            "call",
            "name",
            "phone",
            "email",
            "bussiness",
            "connect",
            "time",
            "additional_support"
        ]
    @staticmethod
    def additional_support_db() -> List[Text]:
        return [
            "không",
            "muốn tư vấn tiếp"
        ]
    @staticmethod
    def call_db() -> List[Text]:
        return [
            "nhận tư vấn qua điện thoại từ bộ phận kinh doanh",
            "chat trực tiếp với tổng đài viên"
        ]
    def slot_mappings(self):
        return {
            "name": [
                self.from_entity(entity="name",not_intent="chitchat"),
            ],
            "phone": [
                self.from_entity(entity="phone",not_intent="chitchat"),
                self.from_text(intent="inform")
            ],
            "email": [
                self.from_entity(entity="email",not_intent="chitchat"),
            ],
            "bussiness": [
                self.from_entity(entity="bussiness",not_intent="chitchat"),
                self.from_text(intent="inform")
            ],
            "connect":[
                self.from_text()
            ],
            "call":[
                self.from_text()
            ]
            # "additional_support":[
            #     self.from_intent(intent="deny",value=False)
            # ]
        }
    # def apply_to(self, tracker: "DialogueStateTracker") -> None:
    #     tracker._reset()
    #     tracker.replay_events()

    def validate(self, dispatcher, tracker, domain):
        result = []
        result.append(ReminderScheduled(intent_name="EXTERNAL_reminder",
                                        trigger_date_time=datetime.datetime.now()
                                        + datetime.timedelta(seconds=30),
                                        name="first_remind",
                                        kill_on_user_message=True))
        slot_values = self.extract_other_slots(dispatcher, tracker, domain)
        value = tracker.latest_message.get("text")
        slot_to_fill = tracker.get_slot("requested_slot")
        
        if slot_to_fill: 
            slot_values.update(self.extract_requested_slot(dispatcher,tracker,domain))
        for slot, value in slot_values.items():
            result.append(SlotSet(slot, value))
        if slot_to_fill == "phone":
            value = tracker.latest_message["entities"] 
            try :  
                phone = value[0]['value']
            except:
                result.append(SlotSet("phone",None))
                #dispatcher.utter_message(template='utter_ask_phone')
            else :
                phone = value[0]['value']
                if self.is_phone(phone):
                    result.append(SlotSet("phone",phone))
                else:
                    result.append(SlotSet("phone",None))      
                # phone = value[0]['value']
                # if phone:
                #     if self.is_phone(phone):
                #         result.append(SlotSet("phone",phone))
                #     else:
                #         result.append(SlotSet("phone",None))
                #         #dispatcher.utter_message(template='utter_ask_phone')
                # else:
                #     result.append(SlotSet("phone",None))
                #     #dispatcher.utter_message(template='utter_ask_phone')
        if slot_to_fill=="time":
            value = tracker.latest_message["entities"] 
            value_=[]
            for x in value:
                value_.append(x['entity'])
            if "day" in value_ and "month" in value_ and "year" in value_ and "hour" in value_:
                for x in value:
                    if x['entity'] == 'day':
                        day = x['value']
                    if x['entity'] == 'month':
                        month = x['value']
                    if x['entity'] == 'year':
                        year = x['value']
                    if x['entity'] == 'hour':
                        hour = x['value']
                        hour = self.convert_tail(hour)
                time = datetime.datetime(int(year),int(month),int(day),int(hour))
                time=time.strftime("%m/%d/%Y, %H:%M:%S")
                result.append(SlotSet("time",time))
            elif "day" in value_ and "month" in value_ and "year" in value_ :
                for x in value:
                    if x['entity'] == 'day':
                        day = x['value']
                    if x['entity'] == 'month':
                        month = x['value']
                    if x['entity'] == 'year':
                        year = x['value']
                time = datetime.datetime(int(year),int(month),int(day))
                time=time.strftime("%m/%d/%Y, %H:%M:%S")
                print(time)
                result.append(SlotSet("time",time))         
            elif "day2" in value_ and "hour" in value_  :
                for x in value:
                    if x['entity'] == 'day2':
                        day2 = x['value']
                        if day2 == "nay":
                            time= datetime.datetime.now()
                        elif day2 == "mai":
                            time= datetime.datetime.now() + datetime.timedelta(days=1)
                        elif day2 == "kia":
                            time = datetime.datetime.now() + datetime.timedelta(days=2)
                    if x['entity'] == 'hour':
                        hour = x['value']
                        hour = self.convert_tail(hour)
                time = time.replace(hour=int(hour),minute=0,second=0)
                time=time.strftime("%m/%d/%Y, %H:%M:%S")
                result.append(SlotSet("time",time))
            else:
                print(',,,,,,')
                result.append(SlotSet("time",None))
            # try:
            #     day = value[0]['value']
            #     month = value[1]['value']
            #     year = value[2]['value']
            # except :
            #     result.append(SlotSet("time",None))
            # else:
            #     day = value[0]['value']
            #     month = value[1]['value']
            #     year = value[2]['value']
            #     time = datetime.datetime(year,month,day)
            #     result.append(SlotSet("time",time))
        if slot_to_fill == "call":
            if value.lower() in self.call_db():
                result.append(SlotSet("call", value))
            else:
                result.append(SlotSet("call",None))
        if slot_to_fill == "additional_support":
            if value.lower() in self.additional_support_db():
                result.append(SlotSet("additional_support", value))
            else:
                result.append(SlotSet("additional_support",None))
        
        
        return result

   

class ActionInactivityScheduler(Action):
    def name(self):
        return "action_inactivity_scheduler"
    def run(self, dispatcher, tracker, domain):
        slot_to_fill = tracker.get_slot("requested_slot")
        dispatcher.utter_template('utter_ask_{}'.format(slot_to_fill),tracker)
        result = []
        result.append(ReminderScheduled(intent_name="EXTERNAL_second",
                                        trigger_date_time=datetime.datetime.now()
                                        + datetime.timedelta(seconds=30),
                                        name="second_remind",
                                        kill_on_user_message=True))  
        return result

class ActionInactivitySchedulerFinal(Action):
    def name(self):
        return "action_inactivity_scheduler_final"
    def run(self, dispatcher, tracker, domain):
        return [Form(None),SlotSet("requested_slot", None)]