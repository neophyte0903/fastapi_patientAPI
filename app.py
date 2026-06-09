from fastapi import FastAPI, Path,HTTPException,Query
from pydantic import BaseModel,EmailStr,AnyUrl,Field, computed_field,field_validator
import json
from typing import List,Dict,Optional,Annotated,Literal
from fastapi.responses import JSONResponse

class Patient(BaseModel):
    id:Annotated[str,Field(...,description='id of the patient',examples=['P001'])]
    name:Annotated[str,Field(...,max_length=50, title="Patient Name", description="Full name of the patient", example="John Doe")]
    city:Annotated[str,Field(...,description="City of residence of the patient", example="New York")]
    age:Annotated[int,Field(...,gt=0, lt=120,description="Age of the patient in years", example=30)]
    gender:Annotated[Literal['male','female','other'],Field(description="Gender of the patient", example="male")]
    height :Annotated[float,Field(...,gt=0, description="Height of the patient in meters", example=1.75)]
    weight:Annotated[float,Field(...,gt=0, description="Weight of the patient in kg", example=70.5)]
    
    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)
    
    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif 18.5 <= self.bmi < 25:
            return 'Normal weight'
        elif 25 <= self.bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'
        
class patient_update(BaseModel):
    name:Annotated[Optional[str],Field(default=None)]
    city:Annotated[Optional[str],Field(default=None)]
    age:Annotated[Optional[int],Field(default=None,gt=0, lt=120)]
    gender:Annotated[Optional[Literal['male','female','other']],Field(default=None)]
    height :Annotated[Optional[float],Field(default=None,gt=0)]
    weight:Annotated[Optional[float],Field(default=None,gt=0)]


app=FastAPI()

#---utlity functions---

def load_data():
    '''helper function to load data from a file or database'''
    with open('patients.json','r') as f:
        data= json.load(f)

    return data

def save_data(data):
    '''helper function to save data to a file or database'''
    with open('patients.json','w') as f:
        json.dump(data,f,indent=4)

@app.get('/') #get request from home route
def hello():
    return {"message":"Patient Management System API"}

@app.get('/about')
def about():
    return {"message":"A fully functional API for managing patient records"}

@app.get('/view')
def view_patients():
    data=load_data()
    return data


@app.get('/patient/{patient_id}')
def view_patient(patient_id:str= Path(..., description="id of paient in DB",example="P001")):
    data=load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail=f"Patient with id {patient_id} not found")

@app.get('/sort')
def sort_patients(sort_by:str= Query(..., description="sort on the basis of height, weight or bmi"),order: str= Query('asc', description ='sort in asc or dsc order')):

    valid_fields=['height','weight','bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail=f"Invalid sort field. Valid fields are {valid_fields}")
    
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400,detail="Invalid sort order. Valid orders are 'asc' and 'desc'")
    
    data=load_data()
    sort_order= True if order=='desc'   else False
    sorted_data=sorted(data.values(),key=lambda x: x.get(sort_by,0),reverse=sort_order)
    return sorted_data

@app.post('/create')
def create_patient(patient:Patient):
    #load existing data
    data=load_data()
    #check if patient with same id already exists
    if patient.id in data:
        raise HTTPException(status_code=400,detail=f"Patient with id {patient.id} already exists")
    #add new patient to data
    data[patient.id]=patient.model_dump(exclude={'id'})
    save_data(data)

    return JSONResponse(status_code=201,content={"message":f"Patient with id {patient.id} created successfully"})

@app.put('/update/{patient_id}')
def update_patient(patient_id:str,patient_update:patient_update):
    data=load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,detail=f"Patient with id {patient_id} not found")
    
    existing_patient=data[patient_id]
    update_data=patient_update.model_dump(exclude_unset=True)
    existing_patient.update(update_data)
    data[patient_id]=existing_patient
    save_data(data)

    return {"message":f"Patient with id {patient_id} updated successfully"}  

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id:str):
    data=load_data()
    if patient_id not in data:
        raise HTTPException(status_code=404,detail=f"Patient with id {patient_id} not found")
    
    del data[patient_id]
    save_data(data)

    return JSONResponse(status_code=200, content={"message": f"Patient with id {patient_id} deleted successfully"})