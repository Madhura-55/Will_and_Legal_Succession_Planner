import os, json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from will_schema import WillData, Asset, Beneficiary

SYSTEM_PROMPT = """You are Smart, a warm and helpful legal assistant guiding Indian families
to create a valid will under the Indian Succession Act 1925 and Hindu Succession Act 1956.
You are part of Smart-Will, an AI-powered will planning service.

Rules you MUST follow:
- Ask EXACTLY ONE question per message. Never ask two questions at once.
- Use simple, friendly language. No legal jargon in questions.
- Adapt questions to family type:
    nuclear: ask about spouse and children
    huf: ask about Karta, coparceners, ancestral vs self-acquired property
    single_parent: ask about guardian for minor children
- After each section, briefly confirm what you understood before moving on.
- When ALL 7 stages are complete, end your final message with the exact token: COLLECTION_COMPLETE

Stages (complete in order):
1. personal_details - name, age, address, religion
2. family_type - nuclear / huf / single_parent
3. assets - immovable property, bank accounts, investments, jewellery
4. beneficiaries - who gets what share
5. executor - who will carry out the will
6. witnesses - two adult names (cannot be beneficiaries)
7. special_wishes - guardian for minors, any residuary clause

Current collected data:
{collected_data}

Current stage: {current_stage}
"""

STAGES = [
    "personal_details",
    "family_type",
    "assets",
    "beneficiaries",
    "executor",
    "witnesses",
    "special_wishes",
    "complete"
]

class ConversationEngine:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=os.environ["GEMINI_API_KEY"],
            temperature=0.3,
            convert_system_message_to_human=True
        )
        self.history = []
        self.will_data = WillData()
        self.stage_index = 0
        self.is_complete = False

    @property
    def current_stage(self):
        return STAGES[self.stage_index]

    def get_will_data(self):
        return self.will_data

    def _build_system(self):
        return SYSTEM_PROMPT.format(
            collected_data=self.will_data.model_dump_json(indent=2),
            current_stage=self.current_stage
        )

    def chat(self, user_message: str) -> str:
        self.history.append(HumanMessage(content=user_message))
        messages = [SystemMessage(content=self._build_system())] + self.history
        response = self.llm.invoke(messages)
        reply = response.content.strip()

        if "COLLECTION_COMPLETE" in reply:
            self.is_complete = True
            self.stage_index = len(STAGES) - 1
            reply = reply.replace("COLLECTION_COMPLETE", "").strip()

        self.history.append(AIMessage(content=reply))
        self._extract_data(user_message)
        self._advance_stage(reply)
        return reply

    def _advance_stage(self, reply: str):
        stage_keywords = {
            "personal_details": ["family", "married", "joint", "single", "nuclear", "hindu"],
            "family_type":      ["property", "asset", "flat", "account", "investment", "gold"],
            "assets":           ["beneficiar", "inherit", "who should", "leave to", "share"],
            "beneficiaries":    ["executor", "carry out", "responsible"],
            "executor":         ["witness", "two adult"],
            "witnesses":        ["guardian", "special wish", "anything else", "residuar"],
        }
        check = reply.lower()
        current = self.current_stage
        if current in stage_keywords:
            if any(k in check for k in stage_keywords[current]):
                if self.stage_index < len(STAGES) - 2:
                    self.stage_index += 1

    def _extract_data(self, user_msg: str):
        extract_prompt = f"""
From the user message below, extract any factual information and return ONLY a JSON object.
Use null for anything not mentioned. Do not include fields you are not sure about.

User message: "{user_msg}"

Return JSON with only these keys (all optional):
{{
  "testator_name": string or null,
  "testator_age": integer or null,
  "testator_address": string or null,
  "religion": string or null,
  "family_type": "nuclear" or "huf" or "single_parent" or null,
  "new_asset": {{ "asset_type": string, "description": string, "identifier": string or null, "estimated_value": number or null }} or null,
  "new_beneficiary": {{ "name": string, "relationship": string, "age": integer, "allocation": string, "is_minor": boolean }} or null,
  "executor_name": string or null,
  "executor_relationship": string or null,
  "new_witness": string or null,
  "minor_guardian": string or null,
  "residuary_beneficiary": string or null
}}

Return ONLY the JSON. No markdown. No explanation.
"""
        try:
            res = self.llm.invoke([HumanMessage(content=extract_prompt)])
            raw = res.content.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            data = json.loads(raw)
            self._merge(data)
        except Exception:
            pass

    def _merge(self, data: dict):
        simple = [
            "testator_name", "testator_age", "testator_address", "religion",
            "family_type", "executor_name", "executor_relationship",
            "minor_guardian", "residuary_beneficiary"
        ]
        for f in simple:
            if data.get(f) is not None:
                setattr(self.will_data, f, data[f])

        if data.get("new_asset"):
            try:
                a = Asset(**data["new_asset"])
                if a.description not in [x.description for x in self.will_data.assets]:
                    self.will_data.assets.append(a)
            except Exception:
                pass

        if data.get("new_beneficiary"):
            try:
                b = Beneficiary(**data["new_beneficiary"])
                if b.name not in [x.name for x in self.will_data.beneficiaries]:
                    self.will_data.beneficiaries.append(b)
            except Exception:
                pass

        if data.get("new_witness"):
            w = data["new_witness"]
            if w and w not in self.will_data.witnesses:
                self.will_data.witnesses.append(w)
