Prerequisites: Python 3.12.6

python3.12 -m venv venv

source venv/bin/activate  # On Windows use `venv\Scripts\activate`

pip install -r reqs.txt

--------------------------------
proto_validation branch

Key Differences and Interactions:

Model-Level Constraints:

Enforced by MongoEngine at database level
Provide hard constraints (unique, required, value ranges)
Cannot be bypassed


Serializer-Level Validations:

Performed before data reaches the database
Can provide more detailed, business-specific validations
Allow for more flexible error messages
Can be bypassed in certain scenarios (like bulk operations)


Validation Sequence:

Serializer validates incoming data
If valid, it calls model's clean() method
Model saves data to database
Database enforces unique and type constraints
--------------------------------
