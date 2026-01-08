import re
import random
import json
from datetime import datetime
import bot  # Import the bot module

# Sample knowledge base for the chatbot
KNOWLEDGE_BASE = {
    "greetings": [
        "Hello! How can I help you with your insurance needs today?",
        "Hi there! I'm InsureBot, your AI insurance assistant. What can I help you with?",
        "Welcome! I'm here to help you find the perfect insurance coverage. What would you like to know?"
    ],
    "farewells": [
        "Thank you for chatting with me today. Feel free to return anytime you have insurance questions!",
        "Have a great day! I'm here whenever you need insurance assistance.",
        "Goodbye! Come back if you have more questions about your insurance options."
    ],
    "thanks": [
        "You're welcome! I'm happy to help with your insurance needs.",
        "Glad I could be of assistance! Let me know if you need anything else.",
        "No problem at all! That's what I'm here for."
    ],
    "insurance_types": {
        "health": "Health insurance covers medical expenses for illnesses, injuries, and preventive care. It typically includes coverage for doctor visits, hospital stays, prescription drugs, and emergency services.",
        "auto": "Auto insurance provides financial protection against physical damage and bodily injury resulting from traffic accidents. It can also cover theft of the vehicle and liability for accidents.",
        "home": "Home insurance protects your home and possessions against damage or theft. It also provides liability coverage for accidents in the home or on the property.",
        "life": "Life insurance pays out a lump sum to your beneficiaries when you die. It helps provide financial security for your loved ones after your passing.",
        "disability": "Disability insurance replaces a portion of your income if you're unable to work due to an illness or injury. It helps cover your expenses when you can't earn an income.",
        "renters": "Renters insurance protects your personal property in a rented dwelling and provides liability coverage. It's similar to home insurance but doesn't cover the building structure."
    },
    "coverage_explanations": {
        "deductible": "A deductible is the amount you pay out of pocket before your insurance starts covering costs. Generally, plans with higher deductibles have lower monthly premiums, and vice versa.",
        "premium": "A premium is the amount you pay to your insurance company regularly (usually monthly) to maintain your coverage. It's essentially the cost of your insurance policy.",
        "copay": "A copay (or copayment) is a fixed amount you pay for a covered healthcare service, usually when you receive the service. For example, you might pay $25 for a doctor visit.",
        "coinsurance": "Coinsurance is the percentage of costs you pay after you've met your deductible. For instance, if your plan has 20% coinsurance, you pay 20% of the cost while your insurance pays 80%.",
        "out_of_pocket_maximum": "The out-of-pocket maximum is the most you'll have to pay for covered services in a policy period (usually a year). After you reach this amount, your insurance pays 100% of covered services.",
        "network": "A network is a group of healthcare providers that have contracted with your insurance company to provide services. Using in-network providers typically results in lower costs.",
        "claim": "A claim is a formal request to your insurance company asking for coverage or reimbursement for a covered loss or policy event.",
        "liability": "In auto and home insurance, liability coverage protects you if you're legally responsible for damage to others' property or injuries to other people."
    }
}

# Pattern matching for user inputs
PATTERNS = {
    "greeting": r"\b(hi|hello|hey|greetings|howdy)\b",
    "farewell": r"\b(bye|goodbye|see you|farewell|exit|quit)\b",
    "thanks": r"\b(thanks|thank you|appreciate|grateful)\b",
    "health_insurance": r"\b(health insurance|medical|healthcare|doctor|hospital|prescription|medicine)\b",
    "auto_insurance": r"\b(auto insurance|car insurance|vehicle|driving|automobile|car|truck|motorcycle)\b",
    "home_insurance": r"\b(home insurance|house|property|dwelling|homeowner)\b",
    "life_insurance": r"\b(life insurance|death benefit|beneficiary|term life|whole life)\b",
    "disability_insurance": r"\b(disability|unable to work|income protection|sick leave)\b",
    "renters_insurance": r"\b(renters insurance|apartment|tenant|landlord)\b",
    "deductible": r"\b(deductible|out of pocket|before insurance pays)\b",
    "premium": r"\b(premium|monthly cost|monthly payment|insurance cost|price|pricing)\b",
    "copay": r"\b(copay|copayment|pay for visit|doctor visit cost)\b",
    "coinsurance": r"\b(coinsurance|percentage|cost sharing)\b",
    "out_of_pocket_maximum": r"\b(out of pocket maximum|maximum out of pocket|oop max)\b",
    "network": r"\b(network|in-network|out-of-network|provider network|doctors in network)\b",
    "claim": r"\b(claim|file a claim|insurance claim|make a claim)\b",
    "liability": r"\b(liability|liable|legally responsible|at fault)\b",
    "prescription": r"\b(prescription|medicine|medication|drug|pharmacy|prescription drug)\b",
    "budget": r"\b(budget|afford|cost|price|monthly payment|payment)\b",
    "comparison": r"\b(compare|comparison|difference|versus|vs|better|best|recommend|recommendation)\b",
    "hospital": r"\b(hospital|medical center|emergency room|er|urgent care|clinic)\b",
    "help": r"\b(help|confused|explain|understand|how does|what is|tell me about)\b"
}

class InsuranceChatbot:
    def __init__(self):
        self.context = {}
        self.last_topic = None
        self.use_ai = True  # Flag to determine whether to use AI or rule-based responses
    
    def get_response(self, user_input):
        """Generate a response based on user input"""
        if not user_input:
            return random.choice(KNOWLEDGE_BASE["greetings"])
        
        user_input = user_input.lower()
        
        # Check for simple patterns that don't need AI
        if re.search(PATTERNS["greeting"], user_input):
            return random.choice(KNOWLEDGE_BASE["greetings"])
        
        if re.search(PATTERNS["farewell"], user_input):
            return random.choice(KNOWLEDGE_BASE["farewells"])
        
        if re.search(PATTERNS["thanks"], user_input):
            return random.choice(KNOWLEDGE_BASE["thanks"])
        
        # Special case for health insurance
        if "tell me about health insurance" in user_input or "about health insurance" in user_input:
            self.last_topic = "health"
            return KNOWLEDGE_BASE["insurance_types"]["health"]
        
        # For all other queries, use the AI assistant if enabled
        if self.use_ai:
            try:
                # Create a context-aware prompt for the AI
                context_prompt = self._build_context_prompt(user_input)
                
                # Get response from the AI
                ai_response = bot.get_ai_response(context_prompt)
                
                # Try to parse JSON response
                try:
                    json_response = json.loads(ai_response)
                    
                    # Check if insurance_criteria exists and is not empty
                    has_search_criteria = False
                    if "insurance_criteria" in json_response and json_response["insurance_criteria"]:
                        has_search_criteria = True
                        
                        # Update context with insurance criteria if available
                        if "coverage_type" in json_response["insurance_criteria"]:
                            self.last_topic = json_response["insurance_criteria"]["coverage_type"]
                            self.context["last_topic"] = self.last_topic
                        
                        # Add other criteria to context
                        for key, value in json_response["insurance_criteria"].items():
                            self.context[key] = value
                    
                    # Add a flag to indicate if this is a search query with criteria
                    response = json_response.get("response", ai_response)
                    if has_search_criteria:
                        return {"response": response, "has_search_criteria": True}
                    else:
                        return response
                
                except json.JSONDecodeError:
                    # If not valid JSON, return the raw response
                    print("Response was not valid JSON, using raw text.")
                    
                    # Update context based on patterns detected
                    self._update_context(user_input)
                    
                    return ai_response
                
            except Exception as e:
                print(f"Error using AI response: {e}")
                # Fall back to rule-based responses
                return self._get_rule_based_response(user_input)
        else:
            # Use rule-based responses
            return self._get_rule_based_response(user_input)
    
    def _build_context_prompt(self, user_input):
        """Build a context-aware prompt for the AI"""
        prompt = f"User query: {user_input}\n\n"
        
        # Add context information if available
        if self.context:
            prompt += "Context:\n"
            if "user_name" in self.context:
                prompt += f"- User's name: {self.context['user_name']}\n"
            if "insurance_types" in self.context and self.context["insurance_types"]:
                types_str = ", ".join(self.context["insurance_types"])
                prompt += f"- User is interested in: {types_str}\n"
            if "monthly_budget" in self.context:
                prompt += f"- User's monthly budget: ${self.context['monthly_budget']}\n"
            if "last_topic" in self.context:
                prompt += f"- Last discussed topic: {self.context['last_topic']}\n"
            if "age" in self.context:
                prompt += f"- User's age: {self.context['age']}\n"
            if "smoke_status" in self.context:
                prompt += f"- Smoking status: {self.context['smoke_status']}\n"
            if "gender" in self.context:
                prompt += f"- Gender: {self.context['gender']}\n"
        
        # Request JSON format
        prompt += "\nRemember to respond with valid JSON as specified in your instructions."
        
        return prompt
    
    def _update_context(self, user_input):
        """Update context based on patterns in user input"""
        # Update last topic based on detected insurance types
        for insurance_type in ["health_insurance", "auto_insurance", "home_insurance", 
                              "life_insurance", "disability_insurance", "renters_insurance"]:
            if re.search(PATTERNS[insurance_type], user_input):
                insurance_key = insurance_type.split("_")[0]
                self.last_topic = insurance_key
                self.context["last_topic"] = insurance_key
                break
    
    def _get_rule_based_response(self, user_input):
        """Get a response using the rule-based system as fallback"""
        # Check for help requests
        if re.search(PATTERNS["help"], user_input):
            return self._handle_help_request(user_input)
        
        # Check for insurance types
        for insurance_type in ["health_insurance", "auto_insurance", "home_insurance", 
                              "life_insurance", "disability_insurance", "renters_insurance"]:
            if re.search(PATTERNS[insurance_type], user_input):
                insurance_key = insurance_type.split("_")[0]
                self.last_topic = insurance_key
                return KNOWLEDGE_BASE["insurance_types"][insurance_key]
        
        # Check for coverage explanations
        for coverage_type in ["deductible", "premium", "copay", "coinsurance", 
                             "out_of_pocket_maximum", "network", "claim", "liability"]:
            if re.search(PATTERNS[coverage_type], user_input):
                self.last_topic = coverage_type
                return KNOWLEDGE_BASE["coverage_explanations"][coverage_type]
        
        # Rest of the existing rule-based logic...
        if re.search(PATTERNS["prescription"], user_input):
            return "Prescription drug coverage varies by plan. Premium Health Plus offers the best prescription coverage with $5/$25/$45 tiers for generic/brand/specialty medications. Value Health Plan has $10/$30/$60 tiers. Would you like to see plans with good prescription coverage?"
        
        if re.search(PATTERNS["budget"], user_input):
            # Try to extract a budget number
            budget_match = re.search(r'\$?(\d+)', user_input)
            if budget_match:
                budget = int(budget_match.group(1))
                self.context["budget"] = budget
                return f"I'll look for insurance plans within your ${budget} budget. Our Basic Health Coverage at $195/month and Economy Auto Plan at $85/month might fit your needs. Would you like to see these plans?"
            else:
                return "What's your monthly budget for insurance? This will help me find plans that fit your financial situation."
        
        if re.search(PATTERNS["comparison"], user_input):
            if "health" in user_input or self.last_topic == "health":
                return "When comparing health insurance plans, Premium Health Plus offers the lowest deductible ($500) and copays ($15 primary care), but has the highest premium at $385/month. Value Health Plan is more balanced at $275/month with a $1,000 deductible. Basic Health Coverage is the most affordable at $195/month but has a $2,500 deductible. Would you like to see a detailed comparison?"
            elif "auto" in user_input or self.last_topic == "auto":
                return "For auto insurance, Safe Driver Auto provides comprehensive coverage with accident forgiveness and roadside assistance for $125/month. Economy Auto Plan offers basic coverage for $85/month without extras like comprehensive coverage. Basic Auto Coverage provides only minimum required coverage for $65/month. Would you like to see a detailed comparison?"
            else:
                return "I can help you compare different insurance plans. Would you be interested in comparing health insurance plans, auto insurance plans, or another type?"
        
        if re.search(PATTERNS["hospital"], user_input):
            if "memorial" in user_input:
                return "Both Premium Health Plus and Value Health Plan include Memorial Hospital in their network. Basic Health Coverage does not include this hospital."
            else:
                return "The network of hospitals varies by plan. Premium Health Plus has the widest network including most major hospitals. Is there a specific hospital you'd like to check for?"
        
        # Default responses based on context
        if self.context.get("last_topic") == "health" or self.last_topic == "health":
            return "Based on our conversation about health insurance, I recommend looking at Premium Health Plus for comprehensive coverage or Value Health Plan for a more budget-friendly option. Would you like details on either of these plans?"
        elif self.context.get("last_topic") == "auto" or self.last_topic == "auto":
            return "Regarding auto insurance, Safe Driver Auto offers the best protection with comprehensive coverage and extras like accident forgiveness. Economy Auto Plan is a good middle option. Would you like to learn more about either of these?"
        
        # General fallback response
        return "I understand you're looking for insurance information. Could you please specify which type of insurance you're interested in (health, auto, home, life, disability, or renters), or what specific coverage aspect you'd like to know more about?"
    
    def _handle_help_request(self, user_input):
        """Handle a help request based on context or specific terms in the query"""
        if "health insurance" in user_input.lower():
            self.last_topic = "health"
            return KNOWLEDGE_BASE["insurance_types"]["health"]
            
        if "plan" in user_input or "insurance" in user_input:
            return "I can help you learn about different insurance plans, compare options, and find the best coverage for your needs. What type of insurance are you interested in? Health, auto, home, life, disability, or renters?"
        
        if "premium" in user_input or "cost" in user_input or "price" in user_input:
            return "Insurance premiums are the regular payments you make to maintain your coverage. They vary based on coverage level, deductibles, your personal situation, and more. Would you like to know about specific plan prices?"
        
        if "deductible" in user_input:
            return "A deductible is the amount you pay out of pocket before your insurance starts covering costs. Lower deductibles typically mean higher monthly premiums. For example, Premium Health Plus has a $500 deductible but costs $385/month."
        
        if "coverage" in user_input:
            return "Insurance coverage refers to what your policy will pay for. Each plan has different coverage levels for various services or scenarios. Would you like to know about coverage for a specific type of insurance?"
        
        # General help response
        return "I'm InsureBot, your AI insurance assistant. I can help you understand insurance options, compare plans, and find the best coverage for your needs. Just ask me about any insurance topic like health, auto, home insurance, or specific terms like deductibles, premiums, or coverage details."


# Simple function to generate chatbot response
def get_chatbot_response(user_input, context=None):
    """Get a response from the chatbot based on user input and context"""
    chatbot = InsuranceChatbot()
    if context:
        chatbot.context = context
        if "last_topic" in context:
            chatbot.last_topic = context["last_topic"]
    
    return chatbot.get_response(user_input) 