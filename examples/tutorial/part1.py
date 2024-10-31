import os

from flou.ltm import LTM

from openai import OpenAI


class BedtimeStoryWriter(LTM):
    name = "bedtime_story_writer_1"

    def run(self, payload=None):
        client = OpenAI()

        story = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": "Write a bedtime story for my children.",
                }
            ],
            model="gpt-4o-mini",
        )

        self.update_state({'story': story.choices[0].message.content})
