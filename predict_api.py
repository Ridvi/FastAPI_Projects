import pandas as pd #type: ignore
from fastapi import FastAPI #type: ignore
from fastapi.responses import JSONResponse # type: ignore
import pickle
from pydantic import BaseModel,Field,computed_field # type: ignore
from typing import Literal,Annotated
import sklearn

with open('model.pkl','rb') as f:
    model=pickle.load(f)


app=FastAPI()

tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]

tier_2_cities = [
    "Jaipur", "Chandigarh", "Indore", "Lucknow", "Patna", "Ranchi", "Visakhapatnam", "Coimbatore",
    "Bhopal", "Nagpur", "Vadodara", "Surat", "Rajkot", "Jodhpur", "Raipur", "Amritsar", "Varanasi",
    "Agra", "Dehradun", "Mysore", "Jabalpur", "Guwahati", "Thiruvananthapuram", "Ludhiana", "Nashik",
    "Allahabad", "Udaipur", "Aurangabad", "Hubli", "Belgaum", "Salem", "Vijayawada", "Tiruchirappalli",
    "Bhavnagar", "Gwalior", "Dhanbad", "Bareilly", "Aligarh", "Gaya", "Kozhikode", "Warangal",
    "Kolhapur", "Bilaspur", "Jalandhar", "Noida", "Guntur", "Asansol", "Siliguri"
]

class UserInput(BaseModel):

    age:Annotated[int,Field(...,description='age of the customer')]
    weight:Annotated[float,Field(...,gt=0,description='weightof the customer')]
    height:Annotated[float,Field(...,gt=0,description='height of the customer')]
    income_lpa:Annotated[float,Field(...,gt=0,description='age of the customer')]
    smoker:Annotated[bool,Field(...,description='is the customer a smoker')]
    city:Annotated[str,Field(...,description='the city where the customer lives')]
    occupation:Annotated[Literal['retired', 'freelancer', 'student', 'government_job','business_owner', 'unemployed', 'private_job'],Field(...,description='occupation of the customer')]


    @computed_field
    @property
    def bmi(self)-> str:
        return self.weight/(self.height**2)
    

    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        if self.smoker and self.bmi > 30:
            return "high"
        elif self.smoker or self.bmi > 27:
            return "medium"
        else:
            return "low"
        
    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 25:
            return "young"
        elif self.age < 45:
            return "adult"
        elif self.age < 60:
            return "middle_aged"
        return "senior"
    
    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3


@app.post('/predict')
def predict_premium(data:UserInput):

    df=pd.DataFrame(
        [{
            'bmi':data.bmi,
            'age_group': data.age_group,
            'lifestyle_risk': data.lifestyle_risk,
            'city_tier': data.city_tier,
            'income_lpa': data.income_lpa,
            'occupation': data.occupation
        }]
    )

    result=model.predict(df)[0]

    return JSONResponse(status_code=200,content=f'Customer is selected for {result} category') 






