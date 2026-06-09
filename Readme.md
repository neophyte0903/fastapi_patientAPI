## Pydantic

Pydantic is a data validation library it is used because data types are losely defined in python
minimum two basemodels are required<br>

<ol>
<li> data input</li>
<li> data output</li>
</ol>
you see the suggestions while typing that is due to pydantic

## Fast API

It corely works on Decorators
decorators improves the functionality of a function
used for enhancement

update endpoint
the update endpoint will work as the edit in data where it will take two parameter

1. Patient_id
2. request body :- {'city':'mumbai'}
   http method is put

approach:-
create new pydantic model
