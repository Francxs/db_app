Prerequisites: Python 3.12.6

python3.12 -m venv venv

source venv/bin/activate  # On Windows use `venv\Scripts\activate`

pip install -r reqs.txt

Branches:
  - Main Branch - Base Code

  - Test Refined - Refactored

  - Proto_Validation 
    - Refactored to include more validation, indexing for serializers 
      and especially base database constraints for models; 
      slightly different inputs for customer, and products (just for this branch)
      while Feedbacks has a dictionary of accepted words (used throughout all branches)


