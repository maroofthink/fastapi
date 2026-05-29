from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field,computed_field
from typing import Annotated,Literal, Optional
import json

app = FastAPI()


class Patient(BaseModel):
    id: Annotated[str, Field(...,description="id of patient", examples=["p2333"])]
    name: Annotated[str, Field(..., description="name of patient", examples=["John Doe"])]
    city: Annotated[str, Field(..., description="city of patient", examples=["Abc city"])]
    age: Annotated[int, Field(..., description="age of patient",examples=["50"],gt=15,lt=60)]
    gender: Annotated[Literal["Male","Female","Others"],Field(...,description="gender of the applicant")]
    height: Annotated[float, Field(...,gt=0,description="hieght should be in meters")]
    weight: Annotated[float, Field(...,gt=0,description="weight should be in kgs")]

    @computed_field
    @property
    def bmi(self)->float:
        bmi = round(self.weight/(self.height**2),2)
        return bmi
    
    @computed_field
    @property
    def verdict(self)->str:
        if self.bmi < 18.5:
            return "under weight"
        elif self.bmi < 24:
            return "normal"
        elif self.bmi < 30:
            return "normal"
        else:
            return "over weight"
        
class PatientUpdate(BaseModel):
    name: Annotated[Optional[str],Field(default=None)]
    city: Annotated[Optional[str],Field(default=None)]
    age: Annotated[Optional[int],Field(default=None, gt=0)]
    gender: Annotated[Optional[Literal["Male","Female","Others"]],Field(default=None)]
    height: Annotated[Optional[float],Field(default=None,gt=0)]
    weight: Annotated[Optional[float],Field(default=None,gt=0)]


@app.get("/")
def hello():
    return {"Message": "Hello World"}


@app.get("/about")

def about():
    return {"Message": "This is my about us page"}

def load_data():
    with open("patients.json", "r") as f:
        data = json.load(f)
        return data
    
def save_data(data):
    with open("patients.json","w") as f:
        json.dump(data,f)

@app.get("/view")
def view():
    data = load_data()
    return data

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(...,description="Id of patient in the db",examples="P2333")):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail="Patient not found")

@app.get('/sort')
def sort_patients(sort_by: str = Query(...,description='sort on this basis of height, weight '
'or bmi'),order: str= Query(description='sort in ascending or descending order')):
    valid_fields = ['heigh','weight','bmi']

    data = load_data();

    if str not in valid_fields:
        raise HTTPException(status_code=400,detail='Invalid field select from {valid_fields}')
    
    if order not in ["asc","desc"]:
        raise HTTPException(status_code=400,detail='order is not provided please select order as asc or desc')
    
    sort_order = True if order=='desc' else False

    sorted_data = sorted(data.values(), key=lambda x: x.get(sort_by, 0), reverse=False)
    
@app.post('/create')
def create_patient(patient: Patient):
    data = load_data()
    
    if patient.id in data:
        raise HTTPException(status_code=400,detail="Patient already exist")
    
    data[patient.id] = patient.model_dump(exclude=['id'])

    save_data(data);

    return JSONResponse(status_code=201,content={"message":"patient as been saved successfully"})

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: PatientUpdate):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    existing_patient_info = data[patient_id]
    
    updated_patient_info = patient_update.model_dump(exclude_unset=True)

    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value
        existing_patient_info['id'] = patient_id
        patient_pydantice_object = Patient(**existing_patient_info)

        existing_patient_info = patient_pydantice_object.model_dump(exclude=patient_id)

        data[patient_id] = existing_patient_info

        save_data(data)

        return JSONResponse(status_code=200, content={"message":"Patient has been updated successfully"})


@app.delete('/delete_patient/{patient_id}')
def delete_patient(patient_id: str):
    data = load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,detail='patient not found')
    
    del data[patient_id]

    save_data(data)
    return JSONResponse(status_code=200,content={"message":"patient has been deleted"})


