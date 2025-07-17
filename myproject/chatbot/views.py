
from django.shortcuts import render, redirect
import google.generativeai as genai
import os
import json


def chatbot_model(request):
    global content_of_all_files

    if request.method == "POST":
        search_input = request.POST.get("searchInput")  

        output = gemini_output(f"{search_input}")
        
        if "json" in output:
            ''' if the data produced by gemini is of json type
            For example -
            output_data.text = 
            `   ``json
            {output_data from gemini}
            ```
            '''

            json_output = output.replace("json","",1).strip()  
            json_output = json_output.replace("```","").strip()
            
            print(json_output)

            # Convert json string (output_data_str) to Python dictonary
            output_data_dict = json.loads(json_output.strip())
            
            return render(request, "chatbot_1.html", {"json_output": output_data_dict})
        
        return render(request, "chatbot_1.html", {"output": output})

    
    return render(request, "chatbot_1.html")


def gemini_output(input):

    # Configure the Gemini API key    
    gemini_api = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=f"{gemini_api}")

    # Instantiate the model once
    model = genai.GenerativeModel("models/gemini-2.0-flash")
    ''' model = 
    response:
    GenerateContentResponse(
        done=True,
        iterator=None,
        result=protos.GenerateContentResponse({
        "candidates": [
            {
            "content": {
                "parts": [
                {
                    "text": "Actual content"
                }
                ],
                "role": "model"
            },
            "finish_reason": "STOP",
            "avg_logprobs": -0.19224199881920448
            }
        ],
        "usage_metadata": {
            "prompt_token_count": 2,
            "candidates_token_count": 208,
            "total_token_count": 210
        },
        "model_version": "gemini-2.0-flash"
        }),
    ) '''

         
    format = {
        "city": "",
        "weather_data": 
                    [{"Date" : "",
                        "Temperature": 31,
                    "Condition": "Partly Cloudy",
                    "Humidity": 78,
                    "Wind speed": 4.7,
                    "Rain": "Yes, light rain expected in the afternoon",
                    "Summary": "For each day if optional"
                    },]
        ,
        "summary":"Overall summary"
    }

    city_name = model.generate_content(f"""                   
    Extract the city name from the following user message. Only return the name of the city. 
    If there's no city mentioned, say 'NA'.
    Message:'{input}'"
    """)
  
    if city_name.text!= 'NA\n':
        weather_data =  real_weather_API(city_name.text)

        if weather_data == None:
            output = model.generate_content(f"""                   
            
            "You are an intelligent and friendly weather assistant chatbot. Your goal is to help users get 
            accurate, real-time weather updates for any city in the world.
                                            
            User input: "{input}" 

            There is no data from OpenWeatherMap for the city sepecified by the user.
            Respond politely and suggest checking the name or trying again.

            """)

            return output.text
        
   
        else:
            json_output = model.generate_content(f"""                   
            
            "You are an intelligent and friendly weather assistant chatbot. Your goal is to help users get 
            accurate, real-time weather updates for any city in the world.
                                            
            User input: "{input}" 
            Based on the following data from OpenWeatherMap, answer the user's query in a conversational way:
            "{weather_data}"
            
            You should:
            - Greet users politely and ask for the city they are interested in.
            - Fetch and display the current temperature, weather condition (e.g., sunny, cloudy), 
              and rain forecast (if any) for that city only at that time only (no extended forecasts).
            - If the user asks, provide extended forecasts, forecast, or weather report (e.g., 5-day or 10-day)
              then provide all the days weather data.
            - Be able to understand casual language like 'Is it going to rain in Mumbai tomorrow?'
            - Always explain your output in a natural, conversational tone.
            - If the city is not found or there's an API error, respond politely and suggest checking the name or trying again.

            Assume integration with the OpenWeatherMap API (or similar) is available. Format responses cleanly 
            using markdown if the platform allows. Avoid technical jargon. Keep it friendly, useful, and mobile-friendly.        
            
            Output format:
            - If it is a weather report, json {format} 
            - No extra text or explanation
            - can add or delete any field based on the input but provide equal no.of fields for all the 
              days if there are muliple weather data for different days.
            - If any required field is missing, just delete that field. No extra text.

            """)

            return json_output.text
        
    else:
        output = model.generate_content(f"""                   
        
        "You are an intelligent and friendly weather assistant chatbot. Your goal is to help users get 
        accurate, real-time weather updates for any city in the world.
                                        
        User input: "{input}" 

        The user did not provide the city name

        
        You should:
        Greet users politely and ask for the city they are interested in.
        Be able to understand casual language like 'Is it going to rain in Mumbai tomorrow?'
        Always explain your output in a natural, conversational tone.

        Assume integration with the OpenWeatherMap API (or similar) is available. Format responses cleanly 
        using markdown if the platform allows. Avoid technical jargon. Keep it friendly, useful, and mobile-friendly.        

        """)
    
   
        return output.text


##  Integrating a real weather API
def real_weather_API(city):
    import requests

    API_KEY =  os.getenv('WEATHER_API_KEY')        # OpenWeatherMap
    CITY = city
    URL_current_weather = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response_1 = requests.get(URL_current_weather)
    
    URL_forecast_weather = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    response_2 = requests.get(URL_forecast_weather)

    if response_1.status_code == 200 and response_2.status_code == 200:
        data = response_1.json()
        forecast_data = response_2.json()
        forecast_list = forecast_data["list"]
        forecast_list_output = []
        '''forecast_list = data["list"]
    
        # Show forecast for the next 5 days at 12:00 PM
        for item in forecast_list:
            if "12:00:00" in item["dt_txt"]:
                date = item["dt_txt"].split(" ")[0]
                temp = item["main"]["temp"]
                desc = item["weather"][0]["description"]
        '''

        for item in forecast_list:
            if "12:00:00" in item["dt_txt"]:
                forecast_list_output.append(item)

        return f"{data} + {forecast_list_output}"
                

    else:
        return None


def clear_chat(request):
    
    return redirect("chatbot_model_1")
