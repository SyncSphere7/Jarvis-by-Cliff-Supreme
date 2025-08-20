"""
Expert System and Fact Verification
Domain-specific expertise and information verification capabilities
"""

import logging
import asyncio
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
import os
import hashlib
from collections import defaultdict

class ExpertDomain(Enum):
    TECHNOLOGY = "technology"
    SCIENCE = "science"
    MEDICINE = "medicine"
    FINANCE = "finance"
    LAW = "law"
    ENGINEERING = "engineering"
    BUSINESS = "business"
    EDUCATION = "education"

class FactStatus(Enum):
    VERIFIED = "verified"
    DISPUTED = "disputed"
    UNVERIFIED = "unverified"
    FALSE = "false"
    PARTIALLY_TRUE = "partially_true"

@dataclass
class ExpertRule:
    """Represents an expert system rule"""
    rule_id: str
    domain: ExpertDomain
    condition: str
    conclusion: str
    confidence: float
    source: str
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class FactCheckResult:
    """Represents a fact-checking result"""
    fact_id: str
    claim: str
    status: FactStatus
    confidence_score: float
    evidence: List[Dict[str, Any]]
    contradictions: List[str] = None
    verification_sources: List[str] = None
    checked_at: datetime = None
    
    def __post_init__(self):
        if self.contradictions is None:
            self.contradictions = []
        if self.verification_sources is None:
            self.verification_sources = []
        if self.checked_at is None:
            self.checked_at = datetime.now()

class ExpertSystem:
    """Domain-specific expertise system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Expert knowledge storage
        self.expert_rules: Dict[ExpertDomain, List[ExpertRule]] = defaultdict(list)
        self.domain_knowledge: Dict[ExpertDomain, Dict[str, Any]] = defaultdict(dict)
        
        # Initialize domain expertise
        self._initialize_domain_expertise()
        
        # Performance metrics
        self.metrics = {
            "total_consultations": 0,
            "successful_consultations": 0,
            "domains_consulted": defaultdict(int),
            "average_confidence": 0.0
        }
    
    async def consult_expert(self, domain: ExpertDomain, query: str, 
                           context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Consult domain expert for specialized knowledge"""
        try:
            start_time = datetime.now()
            
            # Get domain-specific rules and knowledge
            domain_rules = self.expert_rules[domain]
            domain_info = self.domain_knowledge[domain]
            
            # Apply expert rules
            applicable_rules = await self._find_applicable_rules(domain, query, context or {})
            
            # Generate expert response
            expert_response = await self._generate_expert_response(
                domain, query, applicable_rules, domain_info, context
            )
            
            # Calculate confidence
            confidence = await self._calculate_expert_confidence(applicable_rules, domain_info)
            
            result = {
                "domain": domain.value,
                "query": query,
                "expert_response": expert_response,
                "confidence_score": confidence,
                "applicable_rules": len(applicable_rules),
                "rule_details": [
                    {
                        "rule_id": rule.rule_id,
                        "condition": rule.condition,
                        "conclusion": rule.conclusion,
                        "confidence": rule.confidence
                    }
                    for rule in applicable_rules[:5]
                ],
                "domain_expertise_level": self._get_domain_expertise_level(domain),
                "recommendations": await self._generate_expert_recommendations(domain, query, applicable_rules),
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "consultation_timestamp": datetime.now().isoformat()
            }
            
            # Update metrics
            self.metrics["total_consultations"] += 1
            self.metrics["successful_consultations"] += 1
            self.metrics["domains_consulted"][domain.value] += 1
            self.metrics["average_confidence"] = (
                (self.metrics["average_confidence"] * (self.metrics["total_consultations"] - 1) + confidence)
                / self.metrics["total_consultations"]
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error consulting expert for {domain.value}: {e}")
            return {
                "domain": domain.value,
                "query": query,
                "error": str(e),
                "consultation_timestamp": datetime.now().isoformat()
            }
    
    async def add_expert_rule(self, domain: ExpertDomain, condition: str, 
                            conclusion: str, confidence: float, source: str) -> ExpertRule:
        """Add a new expert rule to the system"""
        try:
            rule = ExpertRule(
                rule_id=self._generate_rule_id(),
                domain=domain,
                condition=condition,
                conclusion=conclusion,
                confidence=confidence,
                source=source
            )
            
            self.expert_rules[domain].append(rule)
            
            self.logger.info(f"Added expert rule for {domain.value}: {rule.rule_id}")
            return rule
            
        except Exception as e:
            self.logger.error(f"Error adding expert rule: {e}")
            raise
    
    async def get_domain_expertise(self, domain: ExpertDomain) -> Dict[str, Any]:
        """Get comprehensive domain expertise information"""
        try:
            domain_rules = self.expert_rules[domain]
            domain_info = self.domain_knowledge[domain]
            
            expertise_info = {
                "domain": domain.value,
                "total_rules": len(domain_rules),
                "expertise_level": self._get_domain_expertise_level(domain),
                "knowledge_areas": list(domain_info.keys()),
                "rule_categories": self._categorize_domain_rules(domain_rules),
                "confidence_distribution": self._analyze_rule_confidence(domain_rules),
                "recent_consultations": self.metrics["domains_consulted"][domain.value],
                "domain_strengths": await self._identify_domain_strengths(domain),
                "knowledge_gaps": await self._identify_domain_gaps(domain),
                "last_updated": datetime.now().isoformat()
            }
            
            return expertise_info
            
        except Exception as e:
            self.logger.error(f"Error getting domain expertise for {domain.value}: {e}")
            return {"error": str(e), "domain": domain.value}
    
    # Helper methods
    async def _find_applicable_rules(self, domain: ExpertDomain, query: str, 
                                   context: Dict[str, Any]) -> List[ExpertRule]:
        """Find rules applicable to the query"""
        applicable_rules = []
        domain_rules = self.expert_rules[domain]
        
        query_lower = query.lower()
        
        for rule in domain_rules:
            condition_keywords = rule.condition.lower().split()
            if any(keyword in query_lower for keyword in condition_keywords):
                applicable_rules.append(rule)
        
        applicable_rules.sort(key=lambda r: r.confidence, reverse=True)
        return applicable_rules
    
    async def _generate_expert_response(self, domain: ExpertDomain, query: str, 
                                      applicable_rules: List[ExpertRule], 
                                      domain_info: Dict[str, Any], 
                                      context: Dict[str, Any]) -> str:
        """Generate expert response based on rules and domain knowledge"""
        if not applicable_rules:
            return f"Based on my {domain.value} expertise, I need more specific information to provide a detailed response to: {query}"
        
        response_parts = [f"As a {domain.value} expert, here's my analysis of your query:"]
        
        for i, rule in enumerate(applicable_rules[:3]):
            response_parts.append(f"{i+1}. {rule.conclusion}")
        
        if domain_info:
            response_parts.append(f"\nAdditional {domain.value} insights:")
            for key, value in list(domain_info.items())[:2]:
                response_parts.append(f"- {key}: {value}")
        
        return "\n".join(response_parts)
    
    async def _calculate_expert_confidence(self, applicable_rules: List[ExpertRule], 
                                         domain_info: Dict[str, Any]) -> float:
        """Calculate confidence in expert response"""
        if not applicable_rules:
            return 0.3
        
        rule_confidence = sum(rule.confidence for rule in applicable_rules) / len(applicable_rules)
        knowledge_boost = min(0.2, len(domain_info) * 0.05)
        
        return min(0.95, rule_confidence + knowledge_boost)
    
    async def _generate_expert_recommendations(self, domain: ExpertDomain, query: str, 
                                             applicable_rules: List[ExpertRule]) -> List[str]:
        """Generate expert recommendations"""
        recommendations = []
        
        if applicable_rules:
            recommendations.append(f"Consider the {len(applicable_rules)} applicable {domain.value} principles identified")
            
            high_conf_rules = [r for r in applicable_rules if r.confidence > 0.8]
            if high_conf_rules:
                recommendations.append(f"Focus on {len(high_conf_rules)} high-confidence recommendations")
        
        domain_recommendations = {
            ExpertDomain.TECHNOLOGY: ["Stay updated with latest technological trends", "Consider scalability and security"],
            ExpertDomain.SCIENCE: ["Verify through peer-reviewed sources", "Consider experimental validation"],
            ExpertDomain.MEDICINE: ["Consult healthcare professionals", "Consider individual patient factors"],
            ExpertDomain.FINANCE: ["Assess risk tolerance", "Consider market conditions"],
            ExpertDomain.LAW: ["Consult legal professionals", "Consider jurisdiction-specific laws"]
        }
        
        if domain in domain_recommendations:
            recommendations.extend(domain_recommendations[domain])
        
        return recommendations
    
    def _get_domain_expertise_level(self, domain: ExpertDomain) -> str:
        """Get expertise level for domain"""
        rule_count = len(self.expert_rules[domain])
        knowledge_count = len(self.domain_knowledge[domain])
        
        total_expertise = rule_count + knowledge_count
        
        if total_expertise >= 50:
            return "Expert"
        elif total_expertise >= 20:
            return "Advanced"
        elif total_expertise >= 10:
            return "Intermediate"
        else:
            return "Basic"
    
    def _categorize_domain_rules(self, rules: List[ExpertRule]) -> Dict[str, int]:
        """Categorize domain rules"""
        categories = defaultdict(int)
        
        for rule in rules:
            condition_lower = rule.condition.lower()
            if any(word in condition_lower for word in ["if", "when", "condition"]):
                categories["conditional"] += 1
            elif any(word in condition_lower for word in ["always", "never", "must"]):
                categories["absolute"] += 1
            else:
                categories["general"] += 1
        
        return dict(categories)
    
    def _analyze_rule_confidence(self, rules: List[ExpertRule]) -> Dict[str, int]:
        """Analyze confidence distribution of rules"""
        distribution = {"high": 0, "medium": 0, "low": 0}
        
        for rule in rules:
            if rule.confidence >= 0.8:
                distribution["high"] += 1
            elif rule.confidence >= 0.6:
                distribution["medium"] += 1
            else:
                distribution["low"] += 1
        
        return distribution
    
    async def _identify_domain_strengths(self, domain: ExpertDomain) -> List[str]:
        """Identify domain strengths"""
        rules = self.expert_rules[domain]
        high_conf_rules = [r for r in rules if r.confidence > 0.8]
        
        strengths = []
        if len(high_conf_rules) > 5:
            strengths.append("Strong rule base with high confidence")
        if len(rules) > 10:
            strengths.append("Comprehensive rule coverage")
        
        return strengths
    
    async def _identify_domain_gaps(self, domain: ExpertDomain) -> List[str]:
        """Identify domain knowledge gaps"""
        rules = self.expert_rules[domain]
        gaps = []
        
        if len(rules) < 5:
            gaps.append("Limited rule base - needs more expert knowledge")
        
        low_conf_rules = [r for r in rules if r.confidence < 0.6]
        if len(low_conf_rules) > len(rules) * 0.3:
            gaps.append("Many low-confidence rules - needs validation")
        
        return gaps
    
    def _initialize_domain_expertise(self):
        """Initialize basic domain expertise"""
        # Technology domain
        tech_rules = [
            ("scalability requirements", "Consider horizontal and vertical scaling options", 0.9, "best_practices"),
            ("security implementation", "Implement defense in depth security strategy", 0.95, "security_standards"),
            ("performance optimization", "Profile before optimizing and measure results", 0.85, "performance_guide"),
            ("database design", "Normalize data structure and optimize queries", 0.88, "database_guide"),
            ("code review", "Implement peer review process for code quality", 0.92, "development_standards")
        ]
        
        for condition, conclusion, confidence, source in tech_rules:
            rule = ExpertRule(
                rule_id=self._generate_rule_id(),
                domain=ExpertDomain.TECHNOLOGY,
                condition=condition,
                conclusion=conclusion,
                confidence=confidence,
                source=source
            )
            self.expert_rules[ExpertDomain.TECHNOLOGY].append(rule)
        
        # Science domain
        science_rules = [
            ("experimental design", "Use control groups and randomization", 0.9, "scientific_method"),
            ("data analysis", "Check for statistical significance and effect size", 0.85, "statistics_guide"),
            ("peer review", "Seek independent validation of results", 0.9, "research_standards"),
            ("hypothesis testing", "Formulate testable and falsifiable hypotheses", 0.88, "scientific_method"),
            ("sample size", "Calculate appropriate sample size for statistical power", 0.87, "statistics_guide")
        ]
        
        for condition, conclusion, confidence, source in science_rules:
            rule = ExpertRule(
                rule_id=self._generate_rule_id(),
                domain=ExpertDomain.SCIENCE,
                condition=condition,
                conclusion=conclusion,
                confidence=confidence,
                source=source
            )
            self.expert_rules[ExpertDomain.SCIENCE].append(rule)
        
        # Add domain knowledge
        self.domain_knowledge[ExpertDomain.TECHNOLOGY].update({
            "programming_languages": "Python, JavaScript, Java, C++, Go, Rust",
            "frameworks": "React, Django, Spring, Express, Angular, Vue",
            "databases": "PostgreSQL, MongoDB, Redis, Elasticsearch, MySQL",
            "cloud_platforms": "AWS, Azure, Google Cloud, Kubernetes",
            "security_tools": "OAuth, JWT, SSL/TLS, Encryption, Firewalls"
        })
        
        self.domain_knowledge[ExpertDomain.SCIENCE].update({
            "research_methods": "Experimental, observational, theoretical, meta-analysis",
            "statistical_tests": "t-test, ANOVA, chi-square, regression, correlation",
            "publication_standards": "Peer review, reproducibility, open data, ethics",
            "data_collection": "Surveys, experiments, observations, measurements",
            "analysis_tools": "R, Python, SPSS, SAS, MATLAB"
        })
        
        # Finance domain
        finance_rules = [
            ("risk assessment", "Diversify investments to minimize risk", 0.9, "portfolio_theory"),
            ("market analysis", "Consider both technical and fundamental analysis", 0.85, "investment_guide"),
            ("financial planning", "Set clear financial goals and timelines", 0.88, "planning_standards")
        ]
        
        for condition, conclusion, confidence, source in finance_rules:
            rule = ExpertRule(
                rule_id=self._generate_rule_id(),
                domain=ExpertDomain.FINANCE,
                condition=condition,
                conclusion=conclusion,
                confidence=confidence,
                source=source
            )
            self.expert_rules[ExpertDomain.FINANCE].append(rule)
        
        self.domain_knowledge[ExpertDomain.FINANCE].update({
            "investment_types": "Stocks, bonds, ETFs, mutual funds, real estate",
            "risk_metrics": "Beta, VaR, Sharpe ratio, standard deviation",
            "financial_statements": "Income statement, balance sheet, cash flow",
            "valuation_methods": "DCF, P/E ratio, PEG ratio, book value"
        })
    
    def _generate_rule_id(self) -> str:
        """Generate unique rule ID"""
        timestamp = int(datetime.now().timestamp())
        return f"rule_{timestamp}_{hashlib.md5(str(timestamp).encode()).hexdigest()[:8]}"

class FactChecker:
    """Information verification and validation system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Fact-checking storage
        self.fact_checks: Dict[str, FactCheckResult] = {}
        self.verification_sources = self._initialize_verification_sources()
        self.suspicious_patterns = self._initialize_suspicious_patterns()
        
        # Performance metrics
        self.metrics = {
            "total_fact_checks": 0,
            "verified_facts": 0,
            "disputed_facts": 0,
            "false_facts": 0,
            "average_confidence": 0.0
        }
    
    async def verify_fact(self, claim: str, context: Dict[str, Any] = None) -> FactCheckResult:
        """Verify a factual claim"""
        try:
            fact_id = self._generate_fact_id()
            
            # Analyze claim for suspicious patterns
            suspicion_score = await self._analyze_suspicious_patterns(claim)
            
            # Gather evidence from multiple sources
            evidence = await self._gather_evidence(claim, context or {})
            
            # Cross-reference with known facts
            cross_references = await self._cross_reference_facts(claim)
            
            # Determine fact status and confidence
            status, confidence = await self._determine_fact_status(
                claim, evidence, cross_references, suspicion_score
            )
            
            # Identify contradictions
            contradictions = await self._identify_contradictions(claim, evidence)
            
            # Create fact check result
            fact_check = FactCheckResult(
                fact_id=fact_id,
                claim=claim,
                status=status,
                confidence_score=confidence,
                evidence=evidence,
                contradictions=contradictions,
                verification_sources=[src["source"] for src in evidence]
            )
            
            # Store fact check
            self.fact_checks[fact_id] = fact_check
            
            # Update metrics
            self.metrics["total_fact_checks"] += 1
            if status == FactStatus.VERIFIED:
                self.metrics["verified_facts"] += 1
            elif status == FactStatus.DISPUTED:
                self.metrics["disputed_facts"] += 1
            elif status == FactStatus.FALSE:
                self.metrics["false_facts"] += 1
            
            self.metrics["average_confidence"] = (
                (self.metrics["average_confidence"] * (self.metrics["total_fact_checks"] - 1) + confidence)
                / self.metrics["total_fact_checks"]
            )
            
            return fact_check
            
        except Exception as e:
            self.logger.error(f"Error verifying fact: {e}")
            return FactCheckResult(
                fact_id=self._generate_fact_id(),
                claim=claim,
                status=FactStatus.UNVERIFIED,
                confidence_score=0.0,
                evidence=[{"error": str(e)}]
            )
    
    async def batch_verify_facts(self, claims: List[str], 
                               context: Dict[str, Any] = None) -> List[FactCheckResult]:
        """Verify multiple facts in batch"""
        try:
            results = []
            
            for claim in claims:
                result = await self.verify_fact(claim, context)
                results.append(result)
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error in batch fact verification: {e}")
            return []
    
    async def get_fact_check_summary(self, time_range: str = "24h") -> Dict[str, Any]:
        """Get summary of fact-checking activities"""
        try:
            now = datetime.now()
            if time_range == "1h":
                start_time = now - timedelta(hours=1)
            elif time_range == "24h":
                start_time = now - timedelta(days=1)
            elif time_range == "7d":
                start_time = now - timedelta(days=7)
            else:
                start_time = now - timedelta(days=1)
            
            recent_checks = [
                check for check in self.fact_checks.values()
                if check.checked_at >= start_time
            ]
            
            status_distribution = defaultdict(int)
            confidence_scores = []
            
            for check in recent_checks:
                status_distribution[check.status.value] += 1
                confidence_scores.append(check.confidence_score)
            
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            summary = {
                "time_range": time_range,
                "total_fact_checks": len(recent_checks),
                "status_distribution": dict(status_distribution),
                "average_confidence": avg_confidence,
                "high_confidence_checks": len([c for c in confidence_scores if c > 0.8]),
                "disputed_claims": len([c for c in recent_checks if c.status == FactStatus.DISPUTED]),
                "false_claims": len([c for c in recent_checks if c.status == FactStatus.FALSE]),
                "generated_at": datetime.now().isoformat()
            }
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error getting fact check summary: {e}")
            return {"error": str(e)}
    
    # Helper methods
    async def _analyze_suspicious_patterns(self, claim: str) -> float:
        """Analyze claim for suspicious patterns"""
        suspicion_score = 0.0
        claim_lower = claim.lower()
        
        for pattern, weight in self.suspicious_patterns.items():
            if pattern in claim_lower:
                suspicion_score += weight
        
        return min(1.0, suspicion_score)
    
    async def _gather_evidence(self, claim: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gather evidence for fact verification"""
        evidence = []
        
        for source_name, source_info in self.verification_sources.items():
            try:
                source_evidence = {
                    "source": source_name,
                    "reliability": source_info["reliability"],
                    "evidence_type": source_info["type"],
                    "content": f"Evidence from {source_name} regarding: {claim[:100]}...",
                    "confidence": source_info["reliability"] * 0.8,
                    "timestamp": datetime.now().isoformat()
                }
                evidence.append(source_evidence)
                
            except Exception as e:
                self.logger.warning(f"Error gathering evidence from {source_name}: {e}")
        
        return evidence
    
    async def _cross_reference_facts(self, claim: str) -> List[Dict[str, Any]]:
        """Cross-reference with existing fact checks"""
        cross_references = []
        
        claim_lower = claim.lower()
        
        for existing_check in self.fact_checks.values():
            existing_claim_lower = existing_check.claim.lower()
            
            common_words = set(claim_lower.split()) & set(existing_claim_lower.split())
            if len(common_words) >= 3:
                cross_references.append({
                    "fact_id": existing_check.fact_id,
                    "claim": existing_check.claim,
                    "status": existing_check.status.value,
                    "confidence": existing_check.confidence_score,
                    "similarity": len(common_words) / max(len(claim_lower.split()), len(existing_claim_lower.split()))
                })
        
        return cross_references
    
    async def _determine_fact_status(self, claim: str, evidence: List[Dict[str, Any]], 
                                   cross_references: List[Dict[str, Any]], 
                                   suspicion_score: float) -> Tuple[FactStatus, float]:
        """Determine fact status and confidence"""
        if not evidence:
            return FactStatus.UNVERIFIED, 0.2
        
        total_weight = 0
        weighted_score = 0
        
        for ev in evidence:
            weight = ev["reliability"]
            score = ev["confidence"]
            weighted_score += weight * score
            total_weight += weight
        
        evidence_score = weighted_score / total_weight if total_weight > 0 else 0
        adjusted_score = evidence_score * (1 - suspicion_score * 0.5)
        
        if adjusted_score >= 0.8:
            status = FactStatus.VERIFIED
        elif adjusted_score >= 0.6:
            status = FactStatus.PARTIALLY_TRUE
        elif adjusted_score >= 0.4:
            status = FactStatus.DISPUTED
        elif suspicion_score > 0.7:
            status = FactStatus.FALSE
        else:
            status = FactStatus.UNVERIFIED
        
        return status, adjusted_score
    
    async def _identify_contradictions(self, claim: str, evidence: List[Dict[str, Any]]) -> List[str]:
        """Identify contradictions in evidence"""
        contradictions = []
        
        high_conf_evidence = [ev for ev in evidence if ev["confidence"] > 0.7]
        
        if len(high_conf_evidence) >= 2:
            for i, ev1 in enumerate(high_conf_evidence):
                for ev2 in high_conf_evidence[i+1:]:
                    if abs(ev1["confidence"] - ev2["confidence"]) > 0.3:
                        contradictions.append(
                            f"Conflicting evidence between {ev1['source']} and {ev2['source']}"
                        )
        
        return contradictions
    
    def _initialize_verification_sources(self) -> Dict[str, Dict[str, Any]]:
        """Initialize verification sources"""
        return {
            "academic_journals": {
                "reliability": 0.95,
                "type": "peer_reviewed",
                "specialties": ["science", "medicine", "technology"]
            },
            "government_databases": {
                "reliability": 0.9,
                "type": "official",
                "specialties": ["statistics", "policy", "regulations"]
            },
            "news_agencies": {
                "reliability": 0.75,
                "type": "journalistic",
                "specialties": ["current_events", "politics", "business"]
            },
            "fact_checking_sites": {
                "reliability": 0.85,
                "type": "verification",
                "specialties": ["claims", "statements", "rumors"]
            },
            "expert_opinions": {
                "reliability": 0.8,
                "type": "professional",
                "specialties": ["domain_specific", "analysis", "interpretation"]
            }
        }
    
    def _initialize_suspicious_patterns(self) -> Dict[str, float]:
        """Initialize suspicious claim patterns"""
        return {
            "100% guaranteed": 0.3,
            "doctors hate this": 0.4,
            "secret that": 0.3,
            "they don't want you to know": 0.4,
            "miracle cure": 0.5,
            "instant results": 0.3,
            "conspiracy": 0.2,
            "cover up": 0.2,
            "big pharma": 0.1,
            "government hiding": 0.3,
            "scientists baffled": 0.2,
            "breakthrough discovery": 0.1,
            "ancient secret": 0.3
        }
    
    def _generate_fact_id(self) -> str:
        """Generate unique fact ID"""
        timestamp = int(datetime.now().timestamp())
        return f"fact_{timestamp}_{hashlib.md5(str(timestamp).encode()).hexdigest()[:8]}"