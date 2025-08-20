"""
Helper methods for Universal Translator
"""

import logging
import asyncio
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

from .universal_translator import TranslationMemory, TranslationDomain, TranslationQuality, LocalizationRule

class TranslatorHelpers:
    """Helper methods for the Universal Translator"""
    
    def _initialize_supported_languages(self) -> Dict[str, Dict[str, Any]]:
        """Initialize supported languages with metadata"""
        return {
            "en": {"name": "English", "native_name": "English", "family": "Germanic", "script": "Latin"},
            "es": {"name": "Spanish", "native_name": "Español", "family": "Romance", "script": "Latin"},
            "fr": {"name": "French", "native_name": "Français", "family": "Romance", "script": "Latin"},
            "de": {"name": "German", "native_name": "Deutsch", "family": "Germanic", "script": "Latin"},
            "it": {"name": "Italian", "native_name": "Italiano", "family": "Romance", "script": "Latin"},
            "pt": {"name": "Portuguese", "native_name": "Português", "family": "Romance", "script": "Latin"},
            "ru": {"name": "Russian", "native_name": "Русский", "family": "Slavic", "script": "Cyrillic"},
            "zh": {"name": "Chinese", "native_name": "中文", "family": "Sino-Tibetan", "script": "Chinese"},
            "ja": {"name": "Japanese", "native_name": "日本語", "family": "Japonic", "script": "Japanese"},
            "ko": {"name": "Korean", "native_name": "한국어", "family": "Koreanic", "script": "Hangul"},
            "ar": {"name": "Arabic", "native_name": "العربية", "family": "Semitic", "script": "Arabic"},
            "hi": {"name": "Hindi", "native_name": "हिन्दी", "family": "Indo-European", "script": "Devanagari"}
        }
    
    def _initialize_translation_engines(self) -> Dict[str, Dict[str, Any]]:
        """Initialize translation engine configurations"""
        return {
            "neural_mt": {
                "type": "neural",
                "quality": "high",
                "speed": "medium",
                "supported_domains": ["general", "technical", "business"],
                "max_length": 5000
            },
            "statistical_mt": {
                "type": "statistical",
                "quality": "medium",
                "speed": "fast",
                "supported_domains": ["general"],
                "max_length": 2000
            },
            "rule_based": {
                "type": "rule_based",
                "quality": "medium",
                "speed": "fast",
                "supported_domains": ["technical", "legal"],
                "max_length": 1000
            }
        }
    
    def _initialize_localization_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize built-in localization rules"""
        return {
            "currency_usd_eur": {
                "rule_id": "currency_usd_eur",
                "source_language": "en",
                "target_language": "de",
                "rule_type": "currency",
                "pattern": r"\$(\d+(?:\.\d{2})?)",
                "replacement": r"€\1",
                "description": "Convert USD to EUR format"
            },
            "date_us_eu": {
                "rule_id": "date_us_eu",
                "source_language": "en",
                "target_language": "de",
                "rule_type": "date",
                "pattern": r"(\d{1,2})/(\d{1,2})/(\d{4})",
                "replacement": r"\2.\1.\3",
                "description": "Convert US date format to European"
            },
            "phone_us_intl": {
                "rule_id": "phone_us_intl",
                "source_language": "en",
                "target_language": "de",
                "rule_type": "phone",
                "pattern": r"\((\d{3})\) (\d{3})-(\d{4})",
                "replacement": r"+1 \1 \2 \3",
                "description": "Convert US phone format to international"
            }
        }
    
    async def _load_translation_data(self):
        """Load existing translation data"""
        try:
            trans_file = os.path.join(self.data_dir, "translation_data.json")
            if os.path.exists(trans_file):
                with open(trans_file, 'r') as f:
                    trans_data = json.load(f)
                    
                    # Load translation memory
                    for memory_data in trans_data.get("translation_memory", []):
                        memory_entry = TranslationMemory(
                            source_text=memory_data['source_text'],
                            target_text=memory_data['target_text'],
                            source_language=memory_data['source_language'],
                            target_language=memory_data['target_language'],
                            domain=TranslationDomain(memory_data['domain']),
                            quality_score=memory_data['quality_score'],
                            created_at=datetime.fromisoformat(memory_data['created_at']),
                            usage_count=memory_data.get('usage_count', 0)
                        )
                        self.translation_memory.append(memory_entry)
                        
        except Exception as e:
            self.logger.warning(f"Could not load translation data: {e}")
    
    async def _save_translation_data(self):
        """Save translation data"""
        try:
            trans_data = {
                "translation_memory": [
                    {
                        'source_text': entry.source_text,
                        'target_text': entry.target_text,
                        'source_language': entry.source_language,
                        'target_language': entry.target_language,
                        'domain': entry.domain.value,
                        'quality_score': entry.quality_score,
                        'created_at': entry.created_at.isoformat(),
                        'usage_count': entry.usage_count
                    }
                    for entry in self.translation_memory
                ]
            }
            
            trans_file = os.path.join(self.data_dir, "translation_data.json")
            with open(trans_file, 'w') as f:
                json.dump(trans_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Could not save translation data: {e}")
    
    async def _initialize_language_pairs(self):
        """Initialize supported language pairs"""
        try:
            # Create language pairs for common combinations
            common_pairs = [
                ("en", "es"), ("en", "fr"), ("en", "de"), ("en", "it"), ("en", "pt"),
                ("es", "en"), ("fr", "en"), ("de", "en"), ("it", "en"), ("pt", "en"),
                ("es", "fr"), ("fr", "es"), ("de", "fr"), ("fr", "de")
            ]
            
            for source_lang, target_lang in common_pairs:
                pair_id = f"{source_lang}_{target_lang}"
                if pair_id not in self.language_pairs:
                    self.language_pairs[pair_id] = LanguagePair(
                        source_language=source_lang,
                        target_language=target_lang,
                        quality_level=TranslationQuality.GOOD,
                        supported_domains=[TranslationDomain.GENERAL, TranslationDomain.BUSINESS],
                        confidence_score=0.85
                    )
                    
        except Exception as e:
            self.logger.error(f"Error initializing language pairs: {e}")
    
    async def _perform_language_detection(self, text: str) -> Dict[str, Any]:
        """Perform advanced language detection"""
        try:
            start_time = datetime.now()
            
            # Enhanced language detection with more indicators
            language_indicators = {
                "en": {
                    "common_words": ["the", "and", "is", "in", "to", "of", "a", "that", "it", "with", "for", "as", "was", "on", "are"],
                    "patterns": [r"\bthe\b", r"\band\b", r"\bis\b"],
                    "character_patterns": []
                },
                "es": {
                    "common_words": ["el", "la", "de", "que", "y", "en", "un", "es", "se", "no", "te", "lo", "le", "da", "su"],
                    "patterns": [r"\bel\b", r"\bla\b", r"\bde\b", r"ñ"],
                    "character_patterns": ["ñ", "¿", "¡"]
                },
                "fr": {
                    "common_words": ["le", "de", "et", "à", "un", "il", "être", "et", "en", "avoir", "que", "pour", "dans", "ce", "son"],
                    "patterns": [r"\ble\b", r"\bde\b", r"\bet\b", r"ç"],
                    "character_patterns": ["ç", "é", "è", "à", "ù"]
                },
                "de": {
                    "common_words": ["der", "die", "und", "in", "den", "von", "zu", "das", "mit", "sich", "des", "auf", "für", "ist", "im"],
                    "patterns": [r"\bder\b", r"\bdie\b", r"\bund\b", r"ß"],
                    "character_patterns": ["ß", "ä", "ö", "ü"]
                },
                "it": {
                    "common_words": ["il", "di", "che", "e", "la", "per", "in", "un", "è", "con", "non", "da", "su", "sono", "come"],
                    "patterns": [r"\bil\b", r"\bdi\b", r"\bche\b"],
                    "character_patterns": ["à", "è", "é", "ì", "ò", "ù"]
                },
                "pt": {
                    "common_words": ["o", "de", "e", "do", "da", "em", "um", "para", "é", "com", "não", "uma", "os", "no", "se"],
                    "patterns": [r"\bo\b", r"\bde\b", r"\be\b", r"ã"],
                    "character_patterns": ["ã", "õ", "ç", "á", "é", "í", "ó", "ú"]
                },
                "ru": {
                    "common_words": ["в", "и", "не", "на", "я", "быть", "он", "с", "что", "а", "по", "это", "она", "этот", "к"],
                    "patterns": [r"[а-я]"],
                    "character_patterns": ["а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и"]
                }
            }
            
            text_lower = text.lower()
            words = re.findall(r'\b\w+\b', text_lower)
            
            language_scores = {}
            
            for lang, indicators in language_indicators.items():
                score = 0
                
                # Check common words
                common_word_matches = sum(1 for word in words if word in indicators["common_words"])
                score += common_word_matches / max(1, len(words)) * 0.6
                
                # Check patterns
                pattern_matches = sum(1 for pattern in indicators["patterns"] if re.search(pattern, text_lower))
                score += pattern_matches * 0.2
                
                # Check character patterns
                char_matches = sum(1 for char in indicators["character_patterns"] if char in text_lower)
                score += char_matches * 0.2
                
                language_scores[lang] = score
            
            # Find the language with highest score
            if not language_scores:
                detected_language = "en"
                confidence = 0.5
            else:
                detected_language = max(language_scores, key=language_scores.get)
                confidence = min(1.0, language_scores[detected_language])
            
            # Sort alternatives by score
            alternatives = sorted(
                [(lang, score) for lang, score in language_scores.items() if lang != detected_language],
                key=lambda x: x[1], reverse=True
            )[:3]
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "language": detected_language,
                "confidence": confidence,
                "alternatives": [{"language": lang, "confidence": score} for lang, score in alternatives],
                "processing_time": processing_time
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting language: {e}")
            return {
                "language": "en",
                "confidence": 0.5,
                "alternatives": [],
                "processing_time": 0.0
            }
    
    async def _check_translation_memory(self, text: str, source_lang: str, target_lang: str, domain: str) -> Optional[Dict[str, Any]]:
        """Check translation memory for existing translations"""
        try:
            # Look for exact matches first
            for entry in self.translation_memory:
                if (entry.source_text == text and 
                    entry.source_language == source_lang and 
                    entry.target_language == target_lang and
                    entry.domain.value == domain):
                    
                    # Update usage count
                    entry.usage_count += 1
                    
                    return {
                        "translation": entry.target_text,
                        "quality_score": entry.quality_score,
                        "usage_count": entry.usage_count
                    }
            
            # Look for fuzzy matches (similar text)
            for entry in self.translation_memory:
                if (entry.source_language == source_lang and 
                    entry.target_language == target_lang and
                    entry.domain.value == domain):
                    
                    # Simple similarity check
                    similarity = self._calculate_text_similarity(text, entry.source_text)
                    if similarity > 0.9:  # Very high similarity threshold
                        entry.usage_count += 1
                        return {
                            "translation": entry.target_text,
                            "quality_score": entry.quality_score * similarity,  # Reduce quality for fuzzy match
                            "usage_count": entry.usage_count,
                            "similarity": similarity
                        }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking translation memory: {e}")
            return None
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        try:
            # Simple word-based similarity
            words1 = set(text1.lower().split())
            words2 = set(text2.lower().split())
            
            if not words1 and not words2:
                return 1.0
            if not words1 or not words2:
                return 0.0
            
            intersectiondtranslate  return      
        
 n'd + '\anslateed = trslat       tran'):
     h('\nswitoriginal.end
        if lated + transed = '\n'lat  trans
          n'):h('\.startswitf original        i ' '
 +ed.rstrip()ranslatslated = t   tran     '):
     .endswith('riginal  if o    
  ip()lstr translated.ated = ' ' +     transl       :
with(' ')artsriginal.st if o    
   servationatting preormmple f        # Si"
xt""iginal tem orro fattingreserve form""P"    r:
    r) -> st stslated:tr, tran original: sf,ing(selttve_formaf _preser    
    den
translatiorn improved_ retu        
    ASE)
   OREC=re.IGNation, flagsved_translent, improb', replacemr'\ term + ub(r'\b' +ion = re.sranslatroved_t imp        tems():
   ss_terms.iin busineplacement  term, re     forslation
   on = trand_translati improve           
   }
      ne"
   se "deadli"fr" el= ng =rget_laance" if ta else "échés""eg == anif target_la límite" e": "fech"deadlin        ",
    e "project" els"fr= _lang =targetif jet" lse "pros" eg == "etarget_lan if "proyecto": t"   "projec   
      g","meetin"fr" else = ng =target_laéunion" if lse "r == "es" eang_l" if target "reunióneeting":"m            _terms = {
usiness    bnts
    vemeprorm im te # Business""
       domain"usiness or bslation frove tran """Imp   tr:
     str) -> sng:target_lar, rce_lang: sttr, souanslation: sf, trslation(seltranss_ine_improve_bus def 
    
   nslationed_traprovimn      retur   
       ASE)
 GNOREC flags=re.Ianslation,mproved_tracement, i'\b', repl + term + r.sub(r'\b'reation = ed_translmprov        i
    ems():s.itl_termtechnicament in m, replaceer  for t
      on translati =slationved_tran      impro
            }
   
   orithm""algelse  == "fr" rget_langthme" if tagori" else "al= "es_lang =f targetitmo" i"algorithm":  "algor         r",
  lse "serve "fr" et_lang == targeur" ifvee "ser"es" els ang == target_ldor" if "servir":  "serve          base",
datase "elg == "es" arget_lanif t de datos" "basee":  "databas": "API", "api         = {
  _terms echnical       tent
  improvemvation andeserm preral tTechnic       # ain"""
 dom technical n fore translatio"""Improvr:
        stg: str) -> arget_lanstr, t: rce_langsoun: str, , translatiolf(setranslationcal_chni _improve_te
    defxt
    ted_teurn transla       ret  
 ze()
      ali_text.capittedransla_text = tated      transl     r():
 0].isuppe elif text[()
       text.upperranslated_xt = tnslated_tetra         ():
   perext.isup      elif t  t.title()
_tex translatedlated_text =       trans():
     tleisti text.     ifn
   on patteritalizatiape original cPreserv # 
              phrase)
 e, target_e_phrasurc(soext.replacelated_ttext = transated_     transl):
       ping.items(hrase in mape, target_prce_phras     for sou
   .lower() textt =lated_tex   transons
     slatily tranpp # A            
 {text}"
  ang}] et_lng} to {targ{source_laed from ranslat"[T    return f       ion
 k translatoceric m       # Gen    
 g:appint mif no     
     )
      {}_lang),  targetg,source_lanpings.get((nslation_mapping = tra      mappping
  ion ma translat      # Get        
        }
 }
        "
     "warumy": wann", "whhen": ", "w"wo""where": , "hilfe"help":  leid", " mir "es tutry":   "i'm sor             igung",
 "entschulde":e m"excus, freut mich"et you": " me, "nice to"heiße: "ich is"my name           "
      eißen sie","wie h name": hat is yournen", "w ih es "wie gehtw are you":d", "hoen"guten ab": evening    "good             ,
g"en ta: "guternoon"d aften", "goon morg": "guted morning, "goonein", "no": "s": "ja"ye "             
  ",: "bitte "please""danke",you": "thank n", hewiederse "auf dbye":, "gooo"lo": "hallel         "h {
       ", "de"):     ("en      
      },       oi"
": "pourqu", "whyuand"q "when": e": "où",e", "wherid": "a, "helpé"e suis désol": "j'm sorry "i         
      ,moi"xcusez-e": "e"excuse mhanté", u": "encyoeet o m "nice tle",'appelis": "je m "my name            ,
    ous"z-vs appeleoumment vname": "cour "what is yoous", lez-vnt al": "commee you ar, "howonsoir"": "bgood evening    "        i",
    idrès-mon aprnoon": "b"good afteur", jo"boning": "good morn,  "non"":, "no": "oui""yes       ,
         ît"vous pla"s'il "please":  erci",ou": "m ythankir", "revo"au dbye": oor", "g": "bonjou"hello            {
     ):n", "fr"    ("e   },
                 
""por qué": "why", : "cuándo "when"",: "dóndehere" "w"ayuda", "help": ento",lo si sorry": "       "i'm        
 pe",": "disculuse me, "exco gusto": "muchu"t yoeeice to m, "nllamo": "me y name is"      "m       ?",
   o te llamas": "¿cómr namehat is you "wmo estás?","¿córe you":  "how aches", "buenas noing":ood even    "g      s",
      enas tarde: "buon"rnod afte", "goouenos díasng": "bgood morni", "": "no", "no "sí"yes":           r",
     avopor f": " "please",racias"gnk you": iós", "tha"ad: odbye" "go",": "holaloel        "h  : {
      s")"e",  ("en        gs = {
   inion_mapp  translat      appings
 mensive compreh moregic with lonslationMock tra #               

  text    return    :
    et_langtarg_lang ==   if source
      ns
        latioe mock transplsimusing ,    # For now     ls
PIs or moderanslation A actual tis would use     # Th""
   entation"emlation impltrans""Basic 
        "r:-> st)  strarget_lang:: str, tsource_langt: str, n(self, textionslaic_traasc def _b  asyn
    
     }        r(e)
 ror": st"er                
ence": 0.0,confid          "   0,
   core": 0.ality_s   "qu          ext,
   ext": tslated_t"tran               
 False,ss":     "succe           return {
           on as e:
  pt Exceptiexce
                }
               _based"
 ": "ruleine       "eng
          0.8,":fidence   "con             
re": 0.75,co_sality"qu           
     nslation,": trated_textansla"tr           
     : True,ess"cc"su           
     eturn {     r             
  
    lang)arget_ tng,_lat, sourceation(tex_transl._basicawait selftion =     transla
         try:       """
lationased transform rule-b""Per"        tr, Any]:
[s-> Dict) et_lang: str targlang: str,, source_: strtextelf, ation(ssed_translf _rule_ba async de
    
       }    r(e)
    "error": st         
       ": 0.0,nfidence  "co          
    e": 0.0,ty_scor"quali             
   ": text,d_textateransl    "t         se,
   Faluccess":      "s         {
  rn         retu    as e:
n eptioept Exc exc 
                  }
            ical_mt"
tatistgine": "s       "en        ": 0.75,
 ence   "confid         
    , 0.7":y_score   "qualit           on,
  nslati traed_text":slat"tran           
     s": True,"succes       
          return {            
        )
   arget_langrce_lang, t, souion(textnslatra_tf._basic= await sellation     trans  ry:
      
        tn"""anslatione trical machistatistPerform "        ""y]:
Ant[str, -> Diclang: str) str, target_g: ce_lan: str, sour text(self,lationansatistical_trync def _st
    as
          }     e)
 ": str(  "error     ,
         dence": 0.0  "confi             0,
 ": 0.y_score"qualit             : text,
   t"anslated_tex        "tr      alse,
  ss": F    "succe            eturn {
     r
        as e:tionepcept Excex              
  }
          t"
       "neural_mine":   "eng        5,
     ence": 0.8onfid "c               e": 0.9,
y_scorqualit    "   
         n,ranslatio: base_txt"d_teranslate "t          rue,
     cess": T"suc                return {
        
       
         )arget_langang, tsource_ln, anslation(base_tratios_transle_busines_improv = self.anslationse_tr      ba      
    business":" == in   elif doma      
   t_lang)ang, targee_lurcnslation, so(base_traanslation_trhnicalve_tecelf._impron = sslatiose_tran   ba        al":
     hnic= "tec domain =if          ts
  mprovemenific idomain-specpply   # A       
            ang)
   g, target_lurce_lann(text, soranslatio_t_basicit self.= awaanslation _tr        base  s
  improvementpecific ith domain-sation wslneural tranMock   #       
     try:   ""
    anslation"l machine trrm neurarfoPe"     ""  Any]:
 Dict[str, > r) -main: st: str, doget_lang tarng: str,ce_la sourtext: str,ion(self, _translateural _nef
    async d  
  _mt"]nes["neuralon_engi.translati self      return
      :   else     ]
"atistical_mtines["stnslation_engrn self.tra        retut":
    "drafel == levuality_elif q        "]
eural_mt["nn_enginesranslatiourn self.t  ret       cal"]:
   edil", "mlega in ["or domain" == "nativety_level liqua   if      logic
ction elene smple engi      # Si"
  he task""for tine on engranslatit the best tecel""S "      
 str, Any]:ct[ str) -> Diity_level:, qualin: strtr, domaget_lang: sr, tarang: stlf, source_le(seation_enginransl_telect def _s}
    
           tr(e)
    ": sor  "err            .0,
   0ce":  "confiden            0.0,
   ity_score":    "qual    
        ,t}"Error] {texlation f"[Transxt": anslated_te       "tr    se,
     ": Fal"success                {
  return        
   n: {e}")anslatiovanced tr"Error in adr.error(foggef.l sel       e:
     Exception as except        
          sult
  on_reatisltran return           
    
         )ed_text"]ranslatult["ttion_resxt, translaing(te_formattf._preservesel= t"] slated_tex["tran_resultnslation      tra
          tting:rve_forma if prese       on
    latirocess trans# Post-p              
      )
    langng, target_source_lat, lation(texnse_based_trait self._rulult = awaslation_resan       tr
          else:           et_lang)
_lang, targext, sourceion(t_translatticaltis self._stasult = awaitn_reranslatio          t
      al":atistic= "st"] =ine["typenglif e      e
      g, domain)arget_lang, trce_lan(text, sou_translationelf._neuralit sult = awaesslation_rran       t:
         "== "neural] ["type"  if engine      e type
    on engined  basationnsl Perform tra  #
                   l)
   y_leveitomain, qualet_lang, dng, targource_laine(snslation_engect_traelself._se = ngin e          
 irementsased on requgine benation est transl Select b     #         try:
 "
     " engines"h multiple witranslation advanced tPerform """:
       ct[str, Any] Diool) ->atting: berve_form: str, presevelity_lual, qtr: s   domain                                   
     : str, target_lang: str,lang source_tr,text: stion(self, nslaadvanced_tram_def _perfornc    
    asyy: {e}")
 orlation memo transng tError addif"or(gger.errlolf.   se         on as e:
tiept Exc     excep      
       ta()
      lation_dasave_transself._ await             0:
     % 100 ==emory)n_mranslatiof len(self.t          i
  odicallyisk perio d  # Save t   
              ]
     y[-10000:on_memoratiself.translry = ion_memolattranslf.       se
          10000:ry) >emoslation_mself.tranen(if l          ize
  t memory s Limi #  
                    ntry)
 _eppend(memoryy.aon_memorlatif.trans      sel            

           ))
       now(t=datetime.d_a   create           ore,
  _scityalore=qu_sc  quality           in),
   omaonDomain(d=Translati      domain         
 target_lang,age=angutarget_l              ang,
  e=source_lnguag   source_la        ext,
     target_tet_text=     targ         e_text,
  =sourcurce_text         so(
       nMemoryanslatio Tr =memory_entry         try:
        
   ory"""memslation to tran  """Add at):
      score: floty_ str, qualiomain:str, dlang:  target_str,ource_lang:      s                                  
: str, arget_textstr, t: e_texturcelf, so_memory(sranslationd_to_t def _ad   async  
 turn 0.0
           re{e}")
   ty: larixt siming teticular cal"Error(f.logger.erro    self       :
 n as et Exceptiocep   ex       
       union)
   n(n) / le(intersectio return len         
         
     s2)nion(wordds1.uorunion = w     s2)
       (wordntersection = words1.i