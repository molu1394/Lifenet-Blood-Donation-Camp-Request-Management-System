# lifenet/context_processors.py

def base_template(request):
    if request.user.is_authenticated:
        if hasattr(request.user, "role"):
            if request.user.role == "DONOR":
                return {"base_template": "donors/donors_base.html"}
            elif request.user.role == "PATIENT":
                return {"base_template": "patients/patient_base.html"}
            elif request.user.role == "BLOODBANK":
                return {"base_template": "bloodbanks/bloodbank_base.html"}
            elif request.user.role == "ORG":
                return {"base_template": "organizations/org_base.html"}
            elif request.user.role == "STAFF":
                return {"base_template": "bloodbanks/staff_base.html"}
            elif request.user.role == "ADMIN":
                return {"base_template": "core/core_base.html"}
        
    # Default
    return {"base_template": "homepage.html"}
