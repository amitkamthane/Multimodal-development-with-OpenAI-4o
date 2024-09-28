from datetime import date
import json
import os
import base64

import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from utils import function_call

load_dotenv()
class ProcessImage:
    def openai_init(self):
        """
            Initialize the OpenAI client object.

            Returns:
            obj: The OpenAI client object.
        """
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        return client
    
    def encode_image(self, image_path):
        """
            Encode an image file as a base64 string.

            Parameters:
            image_path (str): The path to the image file to be encoded.

            Returns:
            str: The base64 encoded string of the image.
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")
      
    
    def extract_data_from_receipt(self, base64_image):
        # Encode the image
        
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        # Create the completion request
        print(f"Passing image data to GPT-4o for processing...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a processor of receipts. If the provided image is not a receipt, DON'T DESCRIBE IT! Ask for a receipt."},
                {"role": "user", "content": [
                    {
                        "type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"}
                    }
                ]},
            ],
            tools=function_call,
            tool_choice="auto",
            temperature=0.0,
        )
        print(response)
        return json.loads(response.choices[0].message.tool_calls[0].function.arguments)
    
    def generate_expenses_csv(self, receipt_data):
        # Extract receipt data from the response
        
        # Process each item and append to the DataFrame
        new_rows = []
        for item in receipt_data['items']:

            print(f"Adding item: {item['name']}")
            new_row = {
                "Date": receipt_data.get("date", date.today().isoformat()),
                "Vendor": receipt_data.get("vendor", ""),
                "Name": item.get("name", ""),
                "Quantity": item.get("quantity", 1),
                "Price": item.get("price", 0),
                "Category": item.get("category", "Uncategorized"),
            }
            new_rows.append(new_row)

        # Convert the list of new rows to a DataFrame
        new_rows_df = pd.DataFrame(new_rows)

        print(f"New rows added: {new_rows_df.shape[0]}")
        # Concatenate the new rows DataFrame to the existing expenses DataFrame

        if expenses_df.empty:
            expenses_df = pd.DataFrame()
            expenses_df = new_rows_df
            expenses_df.to_csv('expenses.csv', index=False)
        else:
            expenses_df = pd.concat([expenses_df, new_rows_df], ignore_index=True)
            expenses_df.to_csv('expenses.csv', index=False)

        return expenses_df




  
# client = OpenAI(ProcessImage(api_key=os.environ.get("OPENAI_API_KEY")))
obj = ProcessImage()
IMAGE_PATH = "data/purchase_receipt.jpg"
print(f"Encoding image: {IMAGE_PATH}")
base64_image = obj.encode_image(IMAGE_PATH)
receipt_data =  obj.extract_data_from_receipt(base64_image)
# print(obj.generate_expenses_csv(receipt_data))

        