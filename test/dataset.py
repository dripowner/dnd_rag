from langsmith import Client
import dotenv
import os
import json

dotenv.load_dotenv()

dataset_name = os.getenv("DATASET_NAME")


def load_dataset(dataset_name: str):
    with open(dataset_name, "r", encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":
    client = Client(api_key=os.getenv("LANGCHAIN_API_KEY"))

    dataset = load_dataset("dataset.json")

    ls_dataset = client.create_dataset(dataset_name=dataset_name)

    inputs, outputs = zip(
        *[
            ({"question": example["question"]}, {"answer": example["answer"]})
            for example in dataset
        ]
    )
    client.create_examples(inputs=inputs, outputs=outputs, dataset_id=ls_dataset.id)
