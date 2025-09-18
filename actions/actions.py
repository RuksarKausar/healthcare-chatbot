from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import json

class ActionCheckSymptoms(Action):
    def name(self) -> Text:
        return "action_check_symptoms"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        # Get user message
        user_message = tracker.latest_message['text']
        user_language = tracker.get_slot('user_language') or 'english'
        
        # Simple symptom analysis (you can enhance with ML)
        symptoms = self.extract_symptoms(user_message)
        advice = self.get_health_advice(symptoms, user_language)
        
        dispatcher.utter_message(text=advice)
        
        return []

    def extract_symptoms(self, message: str) -> List[str]:
        # Simple keyword matching - enhance with NER
        symptom_keywords = {
            'fever': ['fever', 'बुखार', 'तेज बुखार'],
            'headache': ['headache', 'head pain', 'सिर दर्द'],
            'cough': ['cough', 'खांसी'],
            'breathing': ['breathing', 'सांस', 'breath'],
        }
        
        found_symptoms = []
        for symptom, keywords in symptom_keywords.items():
            if any(keyword.lower() in message.lower() for keyword in keywords):
                found_symptoms.append(symptom)
        
        return found_symptoms

    def get_health_advice(self, symptoms: List[str], language: str) -> str:
        advice_db = {
            'english': {
                'fever': "🌡️ For fever: Rest, drink fluids, take paracetamol. See doctor if >3 days.",
                'headache': "💊 For headache: Rest in dark room, drink water. Consult doctor if severe.",
                'cough': "😷 For cough: Warm water, honey, avoid cold. See doctor if persistent.",
                'default': "🏥 Please consult a healthcare professional for proper diagnosis."
            },
            'hindi': {
                'fever': "🌡️ बुखार के लिए: आराम करें, पानी पिएं, पैरासिटामोल लें। 3 दिन से ज्यादा हो तो डॉक्टर को दिखाएं।",
                'headache': "💊 सिर दर्द के लिए: अंधेरे में आराम करें, पानी पिएं। तेज दर्द हो तो डॉक्टर से मिलें।",
                'cough': "😷 खांसी के लिए: गर्म पानी, शहद लें, ठंडा न खाएं। लगातार खांसी हो तो डॉक्टर को दिखाएं।",
                'default': "🏥 कृपया सही जांच के लिए किसी स्वास्थ्य कर्मचारी से मिलें।"
            }
        }
        
        if not symptoms:
            return advice_db.get(language, advice_db['english'])['default']
        
        advice_text = ""
        for symptom in symptoms:
            advice_text += advice_db.get(language, advice_db['english']).get(symptom, "") + "\n"
        
        return advice_text or advice_db.get(language, advice_db['english'])['default']


class ActionVaccinationSchedule(Action):
    def name(self) -> Text:
        return "action_vaccination_schedule"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_language = tracker.get_slot('user_language') or 'english'
        
        schedules = {
            'english': """
📅 **Vaccination Schedule**:
👶 **Birth**: BCG, Hepatitis B
🍼 **6 weeks**: DPT-1, OPV-1, Rotavirus-1
📍 **10 weeks**: DPT-2, OPV-2, Rotavirus-2
🎯 **14 weeks**: DPT-3, OPV-3, Rotavirus-3
📊 **9 months**: Measles-1
🎂 **15 months**: MMR, DPT Booster-1
            """,
            'hindi': """
📅 **टीकाकरण कार्यक्रम**:
👶 **जन्म के समय**: BCG, हेपेटाइटिस B
🍼 **6 सप्ताह**: DPT-1, OPV-1, रोटावायरस-1  
📍 **10 सप्ताह**: DPT-2, OPV-2, रोटावायरस-2
🎯 **14 सप्ताह**: DPT-3, OPV-3, रोटावायरस-3
📊 **9 महीने**: खसरा-1
🎂 **15 महीने**: MMR, DPT बूस्टर-1
            """
        }
        
        schedule_text = schedules.get(user_language, schedules['english'])
        dispatcher.utter_message(text=schedule_text)
        
        return []


class ActionGetDiseaseInfo(Action):
    def name(self) -> Text:
        return "action_get_disease_info"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        disease = next(tracker.get_latest_entity_values("disease"), None)
        user_language = tracker.get_slot('user_language') or 'english'
        
        if disease:
            info = self.get_disease_info(disease.lower(), user_language)
            dispatcher.utter_message(text=info)
        else:
            msg = "Please specify which disease you want to know about." if user_language == 'english' else "कृपया बताएं कि आप किस बीमारी के बारे में जानना चाहते हैं।"
            dispatcher.utter_message(text=msg)
        
        return []

    def get_disease_info(self, disease: str, language: str) -> str:
        # Disease information database
        disease_db = {
            'english': {
                'diabetes': "🩺 **Diabetes**: High blood sugar. Prevention: healthy diet, exercise, weight control.",
                'malaria': "🦟 **Malaria**: Mosquito-borne disease. Prevention: mosquito nets, eliminate standing water.",
                'dengue': "🌡️ **Dengue**: Viral fever from mosquitoes. Prevention: clean surroundings, no water stagnation."
            },
            'hindi': {
                'diabetes': "🩺 **मधुमेह**: खून में चीनी की मात्रा बढ़ना। बचाव: संतुलित आहार, व्यायाम, वजन नियंत्रण।",
                'malaria': "🦟 **मलेरिया**: मच्छर से फैलने वाली बीमारी। बचाव: मच्छरदानी, पानी न जमने दें।",
                'dengue': "🌡️ **डेंगू**: मच्छर से फैलने वाला वायरल बुखार। बचाव: साफ-सफाई, पानी न जमाएं।"
            }
        }
        
        return disease_db.get(language, disease_db['english']).get(disease, 
            "Information not available. Please consult a healthcare professional." if language == 'english' 
            else "जानकारी उपलब्ध नहीं। कृपया स्वास्थ्य कर्मचारी से सलाह लें।")