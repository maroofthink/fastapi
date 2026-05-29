from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import pandas as pd
import pickle
import dill


with open("model.pkl", "rb") as f:
    dill.detect.trace(True)
    model = dill.load(f)

app = FastAPI()
tier_1_cities = [
    "Karachi","Lahore","Islamabad","Rawalpindi","Faisalabad"
]

tier_2_cities = [
    "Multan","Peshawar","Hyderabad","Gujranwala","Sialkot","Sargodha","Bahawalpur","Abbottabad","Quetta",
    "Sukkur","Larkana","Mardan","Sheikhupura","Jhelum","Kasur","Rahim Yar Khan","Dera Ghazi Khan","Gujrat","Okara",
    "Wah Cantonment","Mingora","Nawabshah","Mirpur Khas","Chiniot","Khuzdar","Kohat","Muzaffargarh",
    "Sahiwal","Vehari","Attock","Haripur","Burewala","Pakpattan","Turbat","Jacobabad","Jhang",
    "Hafizabad","Khanewal","Mandi Bahauddin","Narowal","Tando Adam","Daska","Kamoke","Swabi","Nowshera","Charsadda","Gilgit","Skardu","Mirpur","Kotli"
]

class UserInput(BaseModel):

    age: Annotated[int, Field(..., gt=0, lt=120, description='Age of the user')]
    weight: Annotated[float, Field(..., gt=0, description='Weight of the user')]
    height: Annotated[float, Field(..., gt=0, lt=2.5, description='Height of the user')]
    income_lpa: Annotated[float, Field(..., gt=0, description='Annual salary of the user in lpa')]
    smoker: Annotated[bool, Field(..., description='Is user a smoker')]
    city: Annotated[str, Field(..., description='The city that the user belongs to')]
    occupation: Annotated[Literal['retired', 'freelancer', 'student', 'government_job',
       'business_owner', 'unemployed', 'private_job'], Field(..., description='Occupation of the user')]
    
    
    @computed_field
    @property
    def bmi(self) -> float:
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
def predict_premium(data: UserInput):
    input_df = pd.DataFrame([{
        'bmi':data.bmi,
        'age_group':data.age_group,
        'lifestyle_risk':data.lifestyle_risk,
        'city_tier':data.city_tier,
        'income_lpa':data.income_lpa,
        'occupation':data.occupation
    }])

    prediction = model.predict(input_df)[0]
    return JSONResponse(status_code=200,content={"predicted_category":prediction})

