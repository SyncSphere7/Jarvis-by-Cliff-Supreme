"""
Supreme Universal Translator
Advanced multi-language translation and localization capabilities.
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime
import os
import hashlib
import re

from ..base_supreme_engine import BaseSupremeEngine, SupremeRequest, SupremeResponse

class TranslationQuality(Enum):
    DRAFT = "draft"
    GOOD = "good"
    PROFESSIONAL = "professional"
    NATIVE = "native"

class TranslationDomain(Enum):
    GENERAL = "general"
    TECHNICAL = "technical"
    MEDICAL = "medical"
    LEGAL = "legal"
    BUSINESS = "business"
    ACADEMIC = "academic"
    CREATIVE = "creative"
    MARKETING = "marketing"

@dataclass
class TranslationMemory:
    """Translation memory entry"""
    source_text: str
    target_text: str
    source_language: str
    target_language: str
    domain: TranslationDomain
    quality_score: float
    created_at: datetime
    usage_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class LanguagePair:
    """Language pair configuration"""
    source_language: str
    target_language: str
    quality_level: TranslationQuality
    supported_domains: List[TranslationDomain]
    confidence_score: float = 0.8

@dataclass
class LocalizationRule:
    """Localization rule for cultural adaptation"""
    rule_id: str
    source_language: str
    target_language: str
    rule_type: str  # currency, date, address, cultural
    pattern: str
    replacement: str
    description: str

class SupremeUniversalTranslator(BaseSupremeEngine):
    """
    Supreme universal translator with advanced multi-language capabilities.
    Provides high-quality translation with cultural localization and domain expertise.
    """
    
    def __init__(self, engine_name: str, config):
        super().__init__(engine_name, config)
        
        # Translation storage
        self.translation_memory: List[TranslationMemory] = []
        self.language_pairs: Dict[str, LanguagePair] = {}
        self.localization_rules: Dict[str, LocalizationRule] = {}
        
        # Translation capabilities
        self.translation_capabilities = {
            "translate_text": self._translate_text,
            "batch_translate": self._batch_translate,
            "detect_language": self._detect_language,
            "get_translation_quality": self._get_translation_quality,
            "localize_content": self._localize_content,
            "manage_translation_memory": self._manage_translation_memory,
            "validate_translation": self._validate_translation
        }
        
        # Supported languages with metadata
        self.supported_languages = self._initialize_supported_languages()
        
        # Translation models and engines
        self.translation_engines = self._initialize_translation_engines()
        
        # Built-in localization rules
        self.builtin_localization_rules = self._initialize_localization_rules()
        
        # Data persistence
        self.data_dir = "data/translation"
        os.makedirs(self.data_dir, exist_ok=True)
    
    async def _initialize_engine(self) -> bool:
        """Initialize the universal translator"""
        try:
            self.logger.info("Initializing Supreme Universal Translator...")
            
            # Load existing translation data
            await self._load_translation_data()
            
            # Initialize language pairs
            await self._initialize_language_pairs()
            
            # Load built-in localization rules
            for rule_id, rule_config in self.builtin_localization_rules.items():
                if rule_id not in self.localization_rules:
                    self.localization_rules[rule_id] = LocalizationRule(**rule_config)
            
            self.logger.info(f"Universal Translator initialized with {len(self.language_pairs)} language pairs")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Universal Translator: {e}")
            return False
    
    async def _execute_operation(self, request: SupremeRequest) -> Any:
        """Execute translation operation"""
        operation = request.operation.lower()
        parameters = request.parameters
        
        # Route to appropriate translation capability
        if "translate" in operation and "batch" not in operation:
            return await self._translate_text(parameters)
        elif "batch" in operation and "translate" in operation:
            return await self._batch_translate(parameters)
        elif "detect" in operation and "language" in operation:
            return await self._detect_language(parameters)
        elif "quality" in operation:
            return await self._get_translation_quality(parameters)
        elif "localize" in operation:
            return await self._localize_content(parameters)
        elif "memory" in operation:
            return await self._manage_translation_memory(parameters)
        elif "validate" in operation:
            return await self._validate_translation(parameters)
        else:
            return await self._get_translator_status(parameters)
    
    async def get_supported_operations(self) -> List[str]:
        """Get supported translation operations"""
        return [
            "translate_text", "batch_translate", "detect_language", "get_translation_quality",
            "localize_content", "manage_translation_memory", "validate_translation", "translator_status"
        ]
    
    async def _translate_text(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Translate text with advanced features"""
        try:
            text = parameters.get("text")
            source_language = parameters.get("source_language", "auto")
            target_language = parameters.get("target_language")
            domain = parameters.get("domain", "general")
            quality_level = parameters.get("quality_level", "good")
            preserve_formatting = parameters.get("preserve_formatting", True)
            use_translation_memory = parameters.get("use_translation_memory", True)
            
            if not text or not target_language:
                return {"error": "text and target_language are required", "operation": "translate_text"}
            
            # Auto-detect source language if needed
            if source_language == "auto":
                detection_result = await self._detect_language({"text": text})
                source_language = detection_result.get("detected_language", "en")
            
            # Check translation memory first
            if use_translation_memory:
                memory_result = await self._check_translation_memory(text, source_language, target_language, domain)
                if memory_result:
                    return {
                        "operation": "translate_text",
                        "source_language": source_language,
                        "target_language": target_language,
                        "original_text": text,
                        "translated_text": memory_result["translation"],
                        "quality_score": memory_result["quality_score"],
                        "source": "translation_memory",
                        "domain": domain,
                        "processing_time": 0.01
                    }
            
            # Perform translation
            start_time = datetime.now()
            translation_result = await self._perform_advanced_translation(
                text, source_language, target_language, domain, quality_level, preserve_formatting
            )
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Store in translation memory
            if translation_result["success"] and use_translation_memory:
                await self._add_to_translation_memory(
                    text, translation_result["translated_text"], 
                    source_language, target_language, domain, translation_result["quality_score"]
                )
            
            result = {
                "operation": "translate_text",
                "source_language": source_language,
                "target_language": target_language,
                "original_text": text,
                "translated_text": translation_result["translated_text"],
                "quality_score": translation_result["quality_score"],
                "confidence": translation_result["confidence"],
                "domain": domain,
                "quality_level": quality_level,
                "processing_time": processing_time,
                "source": "translation_engine",
                "alternatives": translation_result.get("alternatives", [])
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error translating text: {e}")
            return {"error": str(e), "operation": "translate_text"}
    
    async def _batch_translate(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Translate multiple texts in batch"""
        try:
            texts = parameters.get("texts", [])
            source_language = parameters.get("source_language", "auto")
            target_language = parameters.get("target_language")
            domain = parameters.get("domain", "general")
            quality_level = parameters.get("quality_level", "good")
            
            if not texts or not target_language:
                return {"error": "texts and target_language are required", "operation": "batch_translate"}
            
            start_time = datetime.now()
            translation_results = []
            
            # Process each text
            for i, text in enumerate(texts):
                if not text.strip():
                    translation_results.append({
                        "index": i,
                        "original_text": text,
                        "translated_text": text,
                        "quality_score": 1.0,
                        "source_language": source_language,
                        "target_language": target_language
                    })
                    continue
                
                # Translate individual text
                translate_params = {
                    "text": text,
                    "source_language": source_language,
                    "target_language": target_language,
                    "domain": domain,
                    "quality_level": quality_level
                }
                
                translation_result = await self._translate_text(translate_params)
                
                translation_results.append({
                    "index": i,
                    "original_text": text,
                    "translated_text": translation_result.get("translated_text", text),
                    "quality_score": translation_result.get("quality_score", 0.5),
                    "source_language": translation_result.get("source_language", source_language),
                    "target_language": target_language,
                    "error": translation_result.get("error")
                })
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Calculate overall statistics
            successful_translations = len([r for r in translation_results if not r.get("error")])
            average_quality = sum(r["quality_score"] for r in translation_results) / len(translation_results)
            
            result = {
                "operation": "batch_translate",
                "total_texts": len(texts),
                "successful_translations": successful_translations,
                "failed_translations": len(texts) - successful_translations,
                "average_quality_score": average_quality,
                "processing_time": processing_time,
                "domain": domain,
                "quality_level": quality_level,
                "translations": translation_results
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in batch translation: {e}")
            return {"error": str(e), "operation": "batch_translate"}
    
    async def _detect_language(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Detect language with confidence scoring"""
        try:
            text = parameters.get("text")
            
            if not text:
                return {"error": "text is required", "operation": "detect_language"}
            
            # Perform advanced language detection
            detection_result = await self._perform_language_detection(text)
            
            result = {
                "operation": "detect_language",
                "text_sample": text[:100] + "..." if len(text) > 100 else text,
                "detected_language": detection_result["language"],
                "confidence": detection_result["confidence"],
                "language_name": self.supported_languages.get(detection_result["language"], {}).get("name", "Unknown"),
                "alternatives": detection_result["alternatives"],
                "text_length": len(text),
                "processing_time": detection_result["processing_time"]
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error detecting language: {e}")
            return {"error": str(e), "operation": "detect_language"}
    
    async def _get_translation_quality(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Assess translation quality"""
        try:
            source_text = parameters.get("source_text")
            translated_text = parameters.get("translated_text")
            source_language = parameters.get("source_language")
            target_language = parameters.get("target_language")
            
            if not all([source_text, translated_text, source_language, target_language]):
                return {"error": "source_text, translated_text, source_language, and target_language are required", 
                       "operation": "get_translation_quality"}
            
            # Perform quality assessment
            quality_result = await self._assess_translation_quality(
                source_text, translated_text, source_language, target_language
            )
            
            result = {
                "operation": "get_translation_quality",
                "source_language": source_language,
                "target_language": target_language,
                "overall_quality_score": quality_result["overall_score"],
                "quality_metrics": quality_result["metrics"],
                "quality_level": quality_result["quality_level"],
                "issues_detected": quality_result["issues"],
                "suggestions": quality_result["suggestions"],
                "processing_time": quality_result["processing_time"]
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error assessing translation quality: {e}")
            return {"error": str(e), "operation": "get_translation_quality"}
    
    async def _localize_content(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Localize content for target culture"""
        try:
            content = parameters.get("content")
            source_language = parameters.get("source_language")
            target_language = parameters.get("target_language")
            localization_level = parameters.get("localization_level", "standard")  # basic, standard, full
            
            if not all([content, source_language, target_language]):
                return {"error": "content, source_language, and target_language are required", 
                       "operation": "localize_content"}
            
            # Perform localization
            start_time = datetime.now()
            localization_result = await self._perform_localization(
                content, source_language, target_language, localization_level
            )
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "operation": "localize_content",
                "source_language": source_language,
                "target_language": target_language,
                "localization_level": localization_level,
                "original_content": content,
                "localized_content": localization_result["localized_content"],
                "localizations_applied": localization_result["localizations_applied"],
                "cultural_adaptations": localization_result["cultural_adaptations"],
                "processing_time": processing_time
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error localizing content: {e}")
            return {"error": str(e), "operation": "localize_content"}
    
    async def _manage_translation_memory(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Manage translation memory"""
        try:
            action = parameters.get("action", "list")  # list, add, search, delete, export
            
            if action == "list":
                # List translation memory entries
                memory_entries = [
                    {
                        "source_text": entry.source_text[:100] + "..." if len(entry.source_text) > 100 else entry.source_text,
                        "target_text": entry.target_text[:100] + "..." if len(entry.target_text) > 100 else entry.target_text,
                        "source_language": entry.source_language,
                        "target_language": entry.target_language,
                        "domain": entry.domain.value,
                        "quality_score": entry.quality_score,
                        "usage_count": entry.usage_count,
                        "created_at": entry.created_at.isoformat()
                    }
                    for entry in self.translation_memory[-50:]  # Last 50 entries
                ]
                
                return {
                    "operation": "manage_translation_memory",
                    "action": "list",
                    "total_entries": len(self.translation_memory),
                    "entries": memory_entries
                }
            
            elif action == "search":
                # Search translation memory
                query = parameters.get("query", "")
                source_language = parameters.get("source_language")
                target_language = parameters.get("target_language")
                
                matching_entries = []
                for entry in self.translation_memory:
                    if query.lower() in entry.source_text.lower() or query.lower() in entry.target_text.lower():
                        if not source_language or entry.source_language == source_language:
                            if not target_language or entry.target_language == target_language:
                                matching_entries.append({
                                    "source_text": entry.source_text,
                                    "target_text": entry.target_text,
                                    "source_language": entry.source_language,
                                    "target_language": entry.target_language,
                                    "quality_score": entry.quality_score,
                                    "usage_count": entry.usage_count
                                })
                
                return {
                    "operation": "manage_translation_memory",
                    "action": "search",
                    "query": query,
                    "matches_found": len(matching_entries),
                    "matches": matching_entries[:20]  # Limit to 20 results
                }
            
            else:
                return {"error": f"Unknown action: {action}", "operation": "manage_translation_memory"}
                
        except Exception as e:
            self.logger.error(f"Error managing translation memory: {e}")
            return {"error": str(e), "operation": "manage_translation_memory"}
    
    async def _validate_translation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate translation accuracy and consistency"""
        try:
            source_text = parameters.get("source_text")
            translated_text = parameters.get("translated_text")
            source_language = parameters.get("source_language")
            target_language = parameters.get("target_language")
            validation_rules = parameters.get("validation_rules", ["consistency", "completeness", "terminology"])
            
            if not all([source_text, translated_text, source_language, target_language]):
                return {"error": "source_text, translated_text, source_language, and target_language are required", 
                       "operation": "validate_translation"}
            
            # Perform validation
            validation_result = await self._perform_translation_validation(
                source_text, translated_text, source_language, target_language, validation_rules
            )
            
            result = {
                "operation": "validate_translation",
                "source_language": source_language,
                "target_language": target_language,
                "validation_passed": validation_result["passed"],
                "validation_score": validation_result["score"],
                "validation_rules": validation_rules,
                "issues_found": validation_result["issues"],
                "recommendations": validation_result["recommendations"],
                "processing_time": validation_result["processing_time"]
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error validating translation: {e}")
            return {"error": str(e), "operation": "validate_translation"}
    
    async def _get_translator_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get comprehensive translator status"""
        try:
            total_memory_entries = len(self.translation_memory)
            supported_language_count = len(self.supported_languages)
            language_pairs_count = len(self.language_pairs)
            
            # Memory statistics
            memory_by_language = {}
            memory_by_domain = {}
            
            for entry in self.translation_memory:
                lang_pair = f"{entry.source_language}-{entry.target_language}"
                memory_by_language[lang_pair] = memory_by_language.get(lang_pair, 0) + 1
                memory_by_domain[entry.domain.value] = memory_by_domain.get(entry.domain.value, 0) + 1
            
            # Recent activity
            recent_translations = self.translation_memory[-10:] if self.translation_memory else []
            
            result = {
                "operation": "translator_status",
                "supported_languages": supported_language_count,
                "language_pairs": language_pairs_count,
                "translation_memory_entries": total_memory_entries,
                "supported_domains": [domain.value for domain in TranslationDomain],
                "quality_levels": [quality.value for quality in TranslationQuality],
                "memory_by_language_pair": memory_by_language,
                "memory_by_domain": memory_by_domain,
                "recent_translations": [
                    {
                        "source_language": entry.source_language,
                        "target_language": entry.target_language,
                        "domain": entry.domain.value,
                        "quality_score": entry.quality_score,
                        "created_at": entry.created_at.isoformat()
                    }
                    for entry in recent_translations
                ],
                "languages": self.supported_languages
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting translator status: {e}")
            return {"error": str(e), "operation": "translator_status"}