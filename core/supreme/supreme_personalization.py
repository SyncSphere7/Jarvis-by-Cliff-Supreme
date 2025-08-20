"""
Supreme Personalization Engine
Advanced personalization and customization system for supreme AI capabilities
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json

from .supreme_control_interface import SupremeControlInterface, CommandType, SupremeCommand

logger = logging.getLogger(__name__)


class PersonalityTrait(Enum):
    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    PRACTICAL = "practical"
    EMPATHETIC = "empathetic"
    ASSERTIVE = "assertive"
    COLLABORATIVE = "collaborative"
    DETAIL_ORIENTED = "detail_oriented"
    BIG_PICTURE = "big_picture"
    CONSERVATIVE = "conservative"
    INNOVATIVE = "innovative"


class CommunicationStyle(Enum):
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    CONVERSATIONAL = "conversational"
    CONCISE = "concise"
    DETAILED = "detailed"
    ENCOURAGING = "encouraging"
    DIRECT = "direct"


class LearningPreference(Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"
    EXPERIENTIAL = "experiential"
    COLLABORATIVE = "collaborative"
    INDEPENDENT = "independent"
    STRUCTURED = "structured"


class InteractionMode(Enum):
    PROACTIVE = "proactive"
    REACTIVE = "reactive"
    BALANCED = "balanced"
    MINIMAL = "minimal"
    COMPREHENSIVE = "comprehensive"


@dataclass
class UserPreferences:
    user_id: str
    personality_traits: Dict[PersonalityTrait, float]  # 0.0 to 1.0 strength
    communication_style: CommunicationStyle
    learning_preferences: List[LearningPreference]
    interaction_mode: InteractionMode
    preferred_engines: List[str]
    response_complexity: str  # simple, detailed, comprehensive, supreme
    risk_tolerance: float  # 0.0 to 1.0
    privacy_level: str  # low, medium, high, maximum
    notification_preferences: Dict[str, bool]
    customization_level: str  # basic, advanced, expert
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class PersonalityEngine:
    """Manages dynamic personality adaptation based on user preferences and interactions"""
    
    def __init__(self):
        self.personality_profiles: Dict[str, Dict[PersonalityTrait, float]] = {}
        self.adaptation_history: List[Dict[str, Any]] = []
    
    def get_personality_profile(self, user_id: str, preferences: UserPreferences) -> Dict[PersonalityTrait, float]:
        """Get or create personality profile for user"""
        if user_id not in self.personality_profiles:
            # Initialize with user preferences
            profile = {}
            for trait, strength in preferences.personality_traits.items():
                profile[trait] = strength
            
            # Fill in missing traits with defaults
            for trait in PersonalityTrait:
                if trait not in profile:
                    profile[trait] = 0.5  # Neutral default
            
            self.personality_profiles[user_id] = profile
        
        return self.personality_profiles[user_id]
    
    def adapt_personality(self, user_id: str, interaction_feedback: Dict[str, Any]) -> Dict[PersonalityTrait, float]:
        """Adapt personality based on interaction feedback"""
        try:
            profile = self.personality_profiles.get(user_id, {})
            if not profile:
                return {}
            
            # Simple adaptation based on satisfaction
            satisfaction = interaction_feedback.get("satisfaction", 0.5)
            if satisfaction > 0.7:
                # Slightly increase traits that led to satisfaction
                for trait in profile:
                    profile[trait] = min(1.0, profile[trait] + 0.01)
            
            return profile
            
        except Exception as e:
            logger.error(f"Error adapting personality: {e}")
            return self.personality_profiles.get(user_id, {})


class PreferenceManager:
    """Manages user preferences and customization settings"""
    
    def __init__(self):
        self.user_preferences: Dict[str, UserPreferences] = {}
    
    def get_user_preferences(self, user_id: str) -> UserPreferences:
        """Get user preferences, creating defaults if not found"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = self._create_default_preferences(user_id)
        
        return self.user_preferences[user_id]
    
    def _create_default_preferences(self, user_id: str) -> UserPreferences:
        """Create default preferences for a new user"""
        return UserPreferences(
            user_id=user_id,
            personality_traits={
                PersonalityTrait.ANALYTICAL: 0.6,
                PersonalityTrait.PRACTICAL: 0.7,
                PersonalityTrait.EMPATHETIC: 0.6,
                PersonalityTrait.COLLABORATIVE: 0.5
            },
            communication_style=CommunicationStyle.CONVERSATIONAL,
            learning_preferences=[LearningPreference.VISUAL, LearningPreference.EXPERIENTIAL],
            interaction_mode=InteractionMode.BALANCED,
            preferred_engines=["reasoning", "analytics", "communication"],
            response_complexity="detailed",
            risk_tolerance=0.5,
            privacy_level="medium",
            notification_preferences={
                "proactive_suggestions": True,
                "learning_updates": True,
                "system_alerts": True,
                "performance_reports": False
            },
            customization_level="basic"
        )


class SupremePersonalizationEngine:
    """Master personalization engine that coordinates all personalization aspects"""
    
    def __init__(self, control_interface: SupremeControlInterface):
        self.control_interface = control_interface
        self.personality_engine = PersonalityEngine()
        self.preference_manager = PreferenceManager()
        self.personalization_history: List[Dict[str, Any]] = []
    
    async def personalize_interaction(self, user_id: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """Personalize an interaction based on user preferences"""
        try:
            # Get user preferences and personality
            preferences = self.preference_manager.get_user_preferences(user_id)
            personality = self.personality_engine.get_personality_profile(user_id, preferences)
            
            # Apply personalization
            personalized_request = request.copy()
            
            # Apply communication style
            if "response_format" not in personalized_request:
                personalized_request["response_format"] = self._get_response_format(preferences.communication_style)
            
            # Apply complexity preference
            if "complexity" not in personalized_request:
                personalized_request["complexity"] = preferences.response_complexity
            
            #tr(e)}"error": s {  return        )
  mary: {e}"ion sumnalizattting persorror ge"Eor(flogger.err            
eption as e:  except Exc         
     }
               mat()
 _at.isoforpdated.urencesfed": preupdatelast_          "     items()},
 nality.so perstrength init, raength for tstre: trait.valu_traits": {"personality             l,
   acy_leverences.priv": prefeacy_level    "priv       e,
     erancisk_tolences.rce": preferk_toleran"ris              
  omplexity,.response_cencesy": preferexit_complsespon"re            
    de.value,ction_moes.interaeferenc: prction_mode"intera  "        
      ences],ing_preferearnferences.lprein for pref value ": [pref.rencesrning_prefe"lea             .value,
   tion_stylemunicaferences.comtyle": pren_smmunicatio"co         ,
       _id": user "user_id       {
             return   
                 erences)
ser_id, prefrofile(usonality_pine.get_personality_engy = self.perlit   persona    r_id)
     erences(userefget_user_pger.e_manarencelf.prefe= sferences       prey:
             tr"
 r""or usemary fumation snalizrsohensive pet compre"""Ge      Any]:
  ct[str,  -> Distr)er_id: us(self, ummaryation_srsonaliz  def get_pe
    
  r(e)}: sterror"urn {"ret            {e}")
feedback: om rning frf"Error leaogger.error( l           e:
 xception asxcept E
        e  
          format()}w().isodatetime.nomp": "timestarue, applied": Tning_"learturn {    re
                    })
          t()
  formanow().iso: datetime."timestamp"               
 ction_data, interaon_data":ctira      "inte           user_id,
ser_id":  "u           end({
   y.apptoron_hisersonalizati    self.p        ing event
cord learn      # Re    
                _data)
  onteractid, inuser_ipersonality(ne.adapt__engilityelf.persona sty_updates =sonalier    p     a:
       ion_datinteracton" in sfacti if "sati     d
      eedeality if napt person   # Ad
             try:"""
    ionsonalizat perk to improveeedbacr farn from use """Ley]:
       An Dict[str, Any]) ->str, Dict[a: on_dattiracinte: str, er_idk(self, usdbacfrom_feeef learn_    async d   
nced")
 e, "balan_stylmmunicatio(co.getmat_mappingn for retur}
               orward"
ghtfECT: "straiIRStyle.Dnicationmmu    Co       ortive",
 uppGING: "style.ENCOURAmunicationS        Com  ",
  mprehensiveAILED: "coionStyle.DETommunicat   C      mary",
   ISE: "sum.CONCleStyunicationomm      C,
      ly"endONAL: "friNVERSATItyle.COonSmunicati        Comd",
    letaiICAL: "deStyle.TECHNontiunicaomm    C
        ional",onversatCASUAL: "cnStyle.municatioom       Ced",
     ucturL: "strle.FORMAationStynic  Commu           {
g =at_mappin     forme"""
    stylmmunicationsed on coformat ba response "Get      ""  > str:
yle) -onSticatiommun: Cstylen_communicatiof, rmat(sel_fosponse_get_re    def )}
    
r(eror": st"er": False, iedapplonalization_ "persest,est": requd_requonalize"persturn {  re         )
 : {e}"eractionnalizing intrso(f"Error pe.errorger    log        n as e:
Exceptioexcept 
                }
      
          complexity.response_preferencesity": exponse_compl     "res       value,
    style.ation_ces.communiceren preftyle":unication_s "comm        
       tems()},onality.iersrength in pr trait, stfotrength lue: s {trait.vatraits":y_alit"person           
      True,d":ieization_appl  "personal       t,
       ed_requessonalizerst": pqueized_resonal     "per           n {
      retur    
           nes
   erred_engierences.prefpref] = nes"ferred_engi["prequestsonalized_re    per      
      _request:izedrsonal in pees" noted_engineferr if "pr     s
      erenceengine pref Apply 