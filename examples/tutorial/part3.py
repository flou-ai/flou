from datetime import datetime

from openai import OpenAI
from pydantic import BaseModel

from flou.ltm import LTM
from flou.ui import TableWidget, KeyValueWidget


class Story(BaseModel):
    content: str
    title: str
    summary: str


class WritingInstructions(BaseModel):
    writing_instructions: str


class LLM:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = OpenAI()


class WaitingForInstructions(LTM):
    name = "waiting_for_instructions"


class UpdatingInstructions(LLM, LTM):
    name = "update_instructions"

    def run(self, payload):
        """
        You are a children bedtime stories best seller author.

        Your editor, the father of your readers next story is giving you
        requirements on how to write

        Your task is to update the previous writing instructions with the new
        information given. Do not invent any new information just merge the input
        with the previous instructions.

        Previous writing instructions: ""
        """

        previous_instructions = self.root.store["writing_instructions"]
        new_instructions = payload["writing_instructions"]

        update_instructions = self.client.beta.chat.completions.parse(
            messages=[
                {
                    "role": "system",
                    "content": f"""
You are a children bedtime stories best seller author.

Your editor, the father of your readers next story is giving you
requirements on how to write.

Merge the previous writing instructions with the new information.

Previous instructions:
{previous_instructions}
""",
                },
                {
                    "role": "user",
                    "content": f"""
New writing instructions:
{new_instructions}

Now update the instructions with the new information.
""",
                }
            ],
            model="gpt-4o-mini",
            response_format=WritingInstructions,
        )
        self.root.update_store(
            {"writing_instructions": update_instructions.choices[0].message.parsed.writing_instructions}
        )
        self.transition("instructions_updated")


class WritingStory(LLM, LTM):
    name = "writing_story"

    def run(self, payload=None):
        response = self.client.beta.chat.completions.parse(
            messages=[
                {
                    "role": "system",
                    "content": f"""
You are a children bedtime stories best seller author.

Your editor, the father of your readers next story has the following
instructions on how to write:
{self.root.store["writing_instructions"]}
""",
                },
                {
                    "role": "user",
                    "content": "Write a bedtime story.",
                }
            ],
            model="gpt-4o-mini",
            temperature=0.5,
            response_format=Story,
        )

        stories = self.root.store["stories"]
        story = response.choices[0].message.parsed
        story_data = story.model_dump()
        story_data["date"] = datetime.now().isoformat()
        stories.append(story_data)
        self.root.update_store({"stories": stories})
        self.transition("story_written", payload={"story": story_data})


class Idle(LTM):
    name = "idle"


class BedtimeStoryWriter(LTM):
    name = "bedtime_story_writer_3"
    init = [WaitingForInstructions]

    transitions = [
        {
            "from": WaitingForInstructions,
            "label": "update_instructions",
            "to": UpdatingInstructions,
        },
        {"from": UpdatingInstructions, "label": "instructions_updated", "to": Idle},
        {"from": Idle, "label": "write_story", "to": WritingStory},
        {"from": WritingStory, "label": "story_written", "to": Idle},
        {"from": Idle, "label": "update_instructions", "to": UpdatingInstructions},
    ]

    def get_initial_store(self):
        return {
            "writing_instructions": "",
            "stories": [],
        }
    
    def get_ui_widgets(self):
        return [
            KeyValueWidget(
                title="Writing Instructions",
                keys=["writing_instructions"],
            ),
            TableWidget(
                field="stories",
                columns=[
                    {"key": "title", "label": "Title"},
                    {"key": "summary", "label": "Summary"},
                    {"key": "date", "label": "Date Created"}
                ],
                title="Stories"
            )
        ]