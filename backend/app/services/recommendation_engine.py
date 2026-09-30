"""
ChurnSense AI — Retention Recommendation Engine

An original rule-based recommendation engine that generates personalized
retention actions based on a customer's risk profile, churn drivers,
and subscription characteristics.

Design principles:
  1. Each recommendation is explainable (rationale field explains why it was generated)
  2. Recommendations are prioritized by expected impact and specificity
  3. The engine does NOT claim that recommendations will definitely prevent churn
  4. The engine is designed to be extensible — a future ML/RL module can replace
     or augment the rule engine without changing the API

Recommendation categories:
  - contract_upgrade       → Encourage longer-term contract
  - loyalty_incentive      → Reward long-term customers
  - pricing_review         → Address high-cost concerns
  - personalized_support   → Proactive customer success outreach
  - service_resolution     → Resolve known service issues
  - success_outreach       → General engagement for borderline-risk customers
"""

from typing import Any, Dict, List


# ── Recommendation Data Classes ─────────────────────────────────────────────

class RecommendationTemplate:
    def __init__(
        self,
        category: str,
        title: str,
        description: str,
        priority: int = 5,
    ):
        self.category = category
        self.title = title
        self.description = description
        self.priority = priority


# ── Rule Engine ─────────────────────────────────────────────────────────────

class RetentionRecommendationEngine:
    """
    Generates prioritized retention recommendations for a customer prediction.

    Usage:
        engine = RetentionRecommendationEngine()
        recommendations = engine.generate(
            churn_probability=0.78,
            risk_level="high",
            features={"tenure": 5, "contract": "Month-to-month", ...},
            shap_top_factors=[{"feature": "is_month_to_month", ...}],
        )
    """

    def generate(
        self,
        churn_probability: float,
        risk_level: str,
        features: Dict[str, Any],
        shap_top_factors: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations by evaluating all rules against the customer profile.

        Returns a deduplicated, priority-sorted list of recommendation dicts.
        """
        recommendations: List[Dict[str, Any]] = []

        recommendations.extend(self._rule_contract_type(features))
        recommendations.extend(self._rule_short_tenure(features))
        recommendations.extend(self._rule_high_monthly_charges(features))
        recommendations.extend(self._rule_low_service_engagement(features))
        recommendations.extend(self._rule_risk_level_outreach(risk_level, churn_probability))
        recommendations.extend(self._rule_shap_driven(shap_top_factors, features))

        # Deduplicate by category (keep highest priority per category)
        seen_categories = set()
        unique_recs = []
        for rec in sorted(recommendations, key=lambda x: x["priority"]):
            if rec["category"] not in seen_categories:
                seen_categories.add(rec["category"])
                unique_recs.append(rec)

        return unique_recs[:6]  # Return up to 6 recommendations

    # ── Individual rules ─────────────────────────────────────────────────────

    def _rule_contract_type(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rule: If customer is on a month-to-month contract, suggest an upgrade.

        Rationale: Month-to-month contracts have no lock-in period and are strongly
        associated with higher churn probability. Offering annual or two-year plans
        with an incentive (discount or bonus service) may reduce churn intent.
        """
        contract = str(features.get("contract", features.get("contract_type", ""))).lower()
        if "month" in contract:
            return [{
                "category": "contract_upgrade",
                "title": "Offer Annual Plan Upgrade",
                "description": (
                    "Consider offering this customer a personalized annual or two-year plan "
                    "with a promotional discount or complementary service upgrade. "
                    "Longer-term contracts have lower churn rates in subscription businesses."
                ),
                "rationale": (
                    "Customer is on a month-to-month contract, which offers no lock-in. "
                    "This is one of the strongest churn risk signals."
                ),
                "priority": 1,
            }]
        return []

    def _rule_short_tenure(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rule: New customers (tenure ≤ 12 months) are at highest churn risk.

        Rationale: The first 12 months of a subscription are the highest-risk period.
        Early engagement programs significantly improve long-term retention.
        """
        try:
            tenure = float(features.get("tenure", 0))
        except (TypeError, ValueError):
            return []

        if tenure <= 6:
            return [{
                "category": "personalized_support",
                "title": "Initiate New Customer Onboarding Check-in",
                "description": (
                    "This customer has been subscribed for less than 6 months. "
                    "A proactive customer success check-in call or onboarding email "
                    "sequence can significantly improve early-stage retention."
                ),
                "rationale": (
                    f"Customer tenure is {tenure:.0f} months. New customers in the "
                    "first 6 months are statistically at highest churn risk."
                ),
                "priority": 2,
            }]
        elif tenure <= 12:
            return [{
                "category": "personalized_support",
                "title": "Early Retention Engagement",
                "description": (
                    "Customer is in the early retention phase (< 12 months). "
                    "Consider sending a satisfaction survey and offering a feature discovery session."
                ),
                "rationale": f"Customer tenure is {tenure:.0f} months (early-phase customer).",
                "priority": 3,
            }]
        return []

    def _rule_high_monthly_charges(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rule: If monthly charges are high relative to typical plans, offer a pricing review.

        Rationale: Price sensitivity is a common churn driver. Customers on
        high-cost plans who don't perceive sufficient value are more likely to switch.
        The threshold is set at 80 units — this should be calibrated to the specific
        business domain and dataset distribution.
        """
        try:
            monthly = float(features.get("monthly_charges", 0))
        except (TypeError, ValueError):
            return []

        if monthly > 80:
            return [{
                "category": "pricing_review",
                "title": "Personalized Pricing Review",
                "description": (
                    f"This customer's monthly charges (≈{monthly:.0f}) are relatively high. "
                    "Conduct a usage vs. plan-fit review and consider recommending a plan "
                    "that better matches their actual usage to improve perceived value."
                ),
                "rationale": (
                    f"Monthly charges ({monthly:.2f}) exceed the high-cost threshold. "
                    "Price dissatisfaction is a leading churn driver."
                ),
                "priority": 3,
            }]
        return []

    def _rule_low_service_engagement(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rule: Customers using few services have low switching cost and lower engagement.

        Rationale: Low service adoption means lower utility perception and lower
        cost of switching. Proactively introducing underused features can improve
        retention by increasing product stickiness.
        """
        try:
            svc_count = float(features.get("service_count", 0))
        except (TypeError, ValueError):
            return []

        if svc_count <= 1:
            return [{
                "category": "service_resolution",
                "title": "Service Adoption Initiative",
                "description": (
                    "This customer subscribes to very few services, suggesting low product engagement. "
                    "Consider offering a free trial of complementary services or a demo of "
                    "features they haven't yet used."
                ),
                "rationale": (
                    f"Customer uses only {svc_count:.0f} service(s). Low adoption correlates "
                    "with lower switching costs and reduced retention."
                ),
                "priority": 4,
            }]
        return []

    def _rule_risk_level_outreach(
        self, risk_level: str, churn_probability: float
    ) -> List[Dict[str, Any]]:
        """
        Rule: High and critical risk customers should receive direct outreach.

        Note: This recommendation does not guarantee churn prevention.
        It is a suggested action informed by the model prediction.
        """
        if risk_level in ("high", "critical"):
            return [{
                "category": "success_outreach",
                "title": "Urgent Customer Success Outreach",
                "description": (
                    f"Model predicts {churn_probability*100:.0f}% churn probability. "
                    "Assign a customer success representative for a direct conversation "
                    "to understand concerns, gather feedback, and explore retention options. "
                    "Note: This prediction reflects model output and does not guarantee the "
                    "customer will churn."
                ),
                "rationale": (
                    f"Risk level is '{risk_level}' with churn probability "
                    f"{churn_probability*100:.0f}%. Direct intervention is recommended."
                ),
                "priority": 1,
            }]
        elif risk_level == "medium":
            return [{
                "category": "success_outreach",
                "title": "Proactive Satisfaction Check",
                "description": (
                    "Customer shows moderate churn risk. Send a satisfaction survey "
                    "and offer a loyalty reward (e.g., a service upgrade for a month) "
                    "to reinforce positive sentiment."
                ),
                "rationale": f"Risk level is 'medium' (churn probability: {churn_probability*100:.0f}%).",
                "priority": 4,
            }]
        return []

    def _rule_shap_driven(
        self,
        shap_top_factors: List[Dict[str, Any]],
        features: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Rule: Generate recommendations for the top SHAP-identified risk factors.

        This rule inspects the model's top identified risk factors and generates
        targeted recommendations for each recognized pattern.
        """
        recs = []
        for factor in shap_top_factors[:3]:
            feat = factor.get("feature", "")
            if "tech_support" in feat.lower() and factor.get("shap_value", 0) > 0:
                recs.append({
                    "category": "service_resolution",
                    "title": "Offer Tech Support Upgrade",
                    "description": (
                        "The model identified lack of tech support as a churn risk factor. "
                        "Consider offering a complimentary tech support subscription for the next quarter."
                    ),
                    "rationale": "SHAP analysis identified tech support absence as a positive churn contributor.",
                    "priority": 2,
                })
            elif "senior" in feat.lower() and factor.get("shap_value", 0) > 0:
                recs.append({
                    "category": "personalized_support",
                    "title": "Senior Customer Care Program",
                    "description": (
                        "Consider enrolling this customer in a dedicated senior care program "
                        "offering simplified billing, priority support, and usage guidance."
                    ),
                    "rationale": "Customer is a senior citizen — a demographic with distinct support needs.",
                    "priority": 3,
                })
            elif "loyalty_incentive" not in {r["category"] for r in recs} and "tenure" in feat.lower() and factor.get("shap_value", 0) < 0:
                recs.append({
                    "category": "loyalty_incentive",
                    "title": "Loyalty Reward Program",
                    "description": (
                        "Recognize this customer's tenure with a loyalty reward: "
                        "a service upgrade, billing discount, or exclusive feature access."
                    ),
                    "rationale": "Long tenure identified as a protective factor — reinforce with recognition.",
                    "priority": 5,
                })
        return recs
