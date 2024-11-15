import os

from flou.ltm import LTM

from openai import OpenAI


class LLM:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = OpenAI()


class WaitingForSettings(LTM):
    name = "waiting_for_settings"


class UpdatingSettings(LLM, LTM):
    name = "update_settings"

    def run(self, payload):
        """
        You are a children bedtime stories best seller author.

        Your editor, the father of your readers next story is giving you
        requirements on how to write

        Update the previous settings with the new information.
        """

        previous_settings = self.parent.state["settings"]
        new_settings = payload["settings"]

        update_settings = self.client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"""
You are a children bedtime stories best seller author.

Your editor, the father of your readers next story is giving you
requirements on how to write.

Merge the previous settings with the new information.

Previous settings:
{previous_settings}

New settings:
{new_settings}
""",
                }
            ],
            model="gpt-4o-mini",
        )
        self.parent.update_state(
            {"settings": update_settings.choices[0].message.content}
        )
        self.transition("settings_updated")


class WritingStory(LLM, LTM):
    name = "writing_story"

    def run(self, payload=None):
        story = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Write a bedtime story for my children.",
                }
            ],
            model="gpt-4o-mini",
        )

        stories = self.parent.state["stories"]
        stories.append(story.choices[0].message.content)
        self.parent.update_state({"stories": stories})
        self.transition("story_written")


class Idle(LTM):
    name = "idle"


class BedtimeStoryWriter(LTM):
    name = "bedtime_story_writer_2"
    init = [WaitingForSettings]

    transitions = [
        {
            "from": WaitingForSettings,
            "label": "update_settings",
            "to": UpdatingSettings,
        },
        {"from": UpdatingSettings, "label": "settings_updated", "to": Idle},
        {"from": Idle, "label": "write_story", "to": WritingStory},
        {"from": WritingStory, "label": "story_written", "to": Idle},
        {"from": Idle, "label": "update_settings", "to": UpdatingSettings},
    ]

    def get_initial_state(self):
        return {
            "settings": "",
            "stories": [],
        }
