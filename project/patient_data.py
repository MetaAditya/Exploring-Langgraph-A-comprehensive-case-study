

from langgraph.checkpoint.postgres import PostgresSaver

from langgraph.store.postgres import PostgresStore
from langgraph.store.base import BaseStore
from typing import *

user_name='langgraph_user'
user_password='langgraph_password'
database_DB='langgraph_DB'
store = PostgresStore.from_conn_string( f"postgresql://{user_name}:{user_password}@localhost:5432/{database_DB}" )

class NodeCheckpoint:
    #last_subgraph:str
    last_node:str
    completion_status:Literal["completed", "pending"]



########################



def write_to_store(store, namespace:str, key:str, value:NodeCheckpoint):
    
    
    store.put( namespace=namespace, 
            key=key, 
            value=value
            
              )
        
    return None
        



def get_from_store(store, namespace:str, key:str):
    
    user_data={}
    
    try:
   
      user_data=store.get(namespace=namespace, 
              key=key, 
                            
                )
      
      return user_data
        
      
    except Exception as e:
        return {'error':str(e)}
        
        
        

        
    
    
  




###############################################################

patient_1={


"patient_name":"Thor Triptati",
"gender":"Male",
"symptoms": """
        Mild chest discomfort that increases with movement or touch,
        Sharp chest pain that worsens when taking a deep breath (likely musculoskeletal or pleuritic),
        heart-related issue, that needs attention of physician and NOT cardiologist
             

            """,

"last_appointment_date":"12/9/2025",
"age":35


}





patient_2={
  "patient_name": "Bruce Kumar",
  "gender": "Male",
  "symptoms": """
               Decreased urine output,
               Foamy urine for the last 3 days,
               Swelling in ankles and feet,
               Mild flank pain on the right side,
               Persistent high blood pressure,
               Fatigue and loss of appetite
             """,
  "last_appointment_date": "12/15/2025",
  "age": 47
}





patient_3 = {
  "patient_name": "Alicia Vikander",
  "gender": "Female",
  "symptoms": """
                Persistent eye strain, especially after screen use,
                Blurred vision while reading or focusing on distant objects,
                Frequent headaches originating around the eyes,
                Dryness and irritation in both eyes,
                Sensitivity to light (photophobia),
                Occasional redness and watering of the eyes

             """,
  "last_appointment_date": "11 November 2025",
  "age": 38
}


#######################################################
patient_3_slit_lamp_result_inconclusive = {
    "cataract_present": "YES",                # lens change exists
    "cataract_causative": "indeterminate",   # key field
    "laterality": "right",

    "lens_findings": {
        "right_eye": {
            "lens_opacity": "YES",
            "opacity_type": "nuclear",
            "opacity_grade": 1,              # mild
            "visual_axis_involved": "NO",
            "red_reflex": "near_normal"
        },
        "left_eye": {
            "lens_opacity": "NO",
            "opacity_type": "NO",
            "opacity_grade": 0,
            "visual_axis_involved": "NO",
            "red_reflex": "normal"
        }
    },

    "exam_quality": "adequate",

    "clinical_mismatch": "YES",               
    "reason_for_uncertainty": (
        "Mild nuclear cataract present, but degree of lens opacity "
        "does not correlate with reported visual impairment."
    ),

    "recommendation": "Visual Field Test"
}


patient_3_slit_lamp_result_conclusive =  {
    "cataract_present": "YES",
    "cataract_causative": "YES",
    "laterality": "right",
    "lens_findings": {
        "right_eye": {
            "lens_opacity": "YES",
            "opacity_type": "nuclear",
            "opacity_grade": 3,
            "visual_axis_involved": "YES",
            "red_reflex": "reduced"
        },
        "left_eye": {
            "lens_opacity": "NO",
            "opacity_type": "NO",
            "opacity_grade": 0,
            "visual_axis_involved": "NO",
            "red_reflex": "normal"
        }
    },
    "exam_quality": "adequate",
    "clinical_mismatch": "NO",
    "notes": "Moderate nuclear cataract in right eye fully explains visual loss"
}



patient_3_visual_field_result_inconclusive  = {
    "test_type": "automated_perimetry",
    "test_reliability": "good",              # good | fair | poor

    "laterality": "right",

    "field_findings": {
        "right_eye": {
            "visual_field_defect": "YES",
            "defect_pattern": "central_scotoma",  
            # central_scotoma | arcuate | altitudinal | hemianopia | generalized_depression
            "defect_severity": "moderate",
            "mean_deviation_dB": -7.5,
            "pattern_standard_deviation": "elevated"
        },
        "left_eye": {
            "visual_field_defect": "NO",
            "mean_deviation_dB": -0.8,
            "pattern_standard_deviation": "normal"
        }
    },

    "cataract_effect_likely": "NO",          # 🔑
    "interpretation": (
        "Visual field defect pattern is focal and asymmetric, "
        "not consistent with lenticular opacity."
    ),

    "suspected_pathology": "optic_nerve_or_macular",
    "recommendation": "Further evaluation of optic nerve and retina"
}






patient_3_visual_field_result_conclusive = {
    "test_type": "automated_perimetry",
    "test_reliability": "good",
    "laterality": "right",

    "field_findings": {
        "right_eye": {
            "visual_field_defect": "YES",
            "defect_pattern": "generalized_depression",
            "defect_severity": "mild_to_moderate",
            "mean_deviation_dB": -3.5,
            "pattern_standard_deviation": "normal"
        },
        "left_eye": {
            "visual_field_defect": "NO",
            "mean_deviation_dB": -0.5,
            "pattern_standard_deviation": "normal"
        }
    },

    "cataract_effect_likely": "YES",          # 🔑 confirms lens is cause
    "interpretation": (
        "Visual field shows mild generalized depression in the right eye, "
        "consistent with lenticular opacity (cataract). No focal or asymmetric defects noted."
    ),

    "suspected_pathology": "NO",           # nothing else suspected
    "recommendation": "Cataract in right eye is the primary cause of vision loss"
}








patient_3_retina_conclusive =  {
    "exam_type": "fundus_exam",        # or "OCT" if using OCT imaging
    "laterality": "right",

    "retinal_findings": {
        "right_eye": {
            "optic_disc": "normal",
            "macula": "normal",
            "vessels": "normal",
            "periphery": "normal",
            "lesions": "NO"
        },
        "left_eye": {
            "optic_disc": "normal",
            "macula": "normal",
            "vessels": "normal",
            "periphery": "normal",
            "lesions": "NO"
        }
    },

    "clinical_interpretation": (
        "Retina appears normal in both eyes. No signs of macular degeneration, "
        "retinal vascular disease, or other retinal pathology."
    ),

    "retina_causative_of_vision_loss": "NO",  # 🔑
    "recommendation": "No retinal pathology contributing to vision loss"
}



patient_3_OCT_conclusive = {
    "test_type": "OCT",
    "laterality": "right",

    "macula_status": "normal",
    "optic_nerve_rnfl_thickness_um": 100,       # within normal range
    "optic_nerve_status": "normal",             # normal structure
    "ganglion_cell_layer_status": "normal",
    "peripapillary_rnfl_symmetry": "normal",    # right vs left comparison

    "image_quality": "good",                     # good | fair | poor

    "interpretation": (
        "Optic nerve head, retinal nerve fiber layer, and macula appear normal. "
        "No evidence of glaucomatous or other neuro-ophthalmic pathology."
    ),

    "nerve_pathology_suspected": "NO",         # 🔑 confirms no neural problem
    "recommendation": "No neuro-ophthalmic cause of vision loss detected."
}

############################## Blood and ECG data #############################
patient_3_normal_blood_test = {
    "hemoglobin": 14.2,        # g/dL | Normal: M 13.5–17.5, F 12–15.5 | Within normal limits
    "wbc": 7200,               # /µL  | Normal: 4,000–11,000 | Within normal limits
    "platelets": 265000,       # /µL  | Normal: 150,000–450,000 | Within normal limits
    "rbc": 4.9,                # million/µL | Normal: M 4.7–6.1, F 4.2–5.4 | Within normal limits
    "hematocrit": 42.5,        # %    | Normal: M 41–53, F 36–46 | Within normal limits
    "mcv": 88,                 # fL   | Normal: 80–100 | Within normal limits
    "mch": 29.5,               # pg   | Normal: 27–33 | Within normal limits
    "mchc": 33.8,              # g/dL | Normal: 32–36 | Within normal limits
    "rdw": 13.1,               # %    | Normal: 11.5–14.5 | Within normal limits
    "fasting_glucose": 92,     # mg/dL | Normal: 70–99 | Within normal limits
    "creatinine": 0.9,         # mg/dL | Normal: 0.7–1.3 | Within normal limits
    "urea": 28,                # mg/dL | Normal: 15–40 | Within normal limits
    "sodium": 140,             # mmol/L | Normal: 135–145 | Within normal limits
    "potassium": 4.2           # mmol/L | Normal: 3.5–5.1 | Within normal limits
}

patient_3_abnormal_blood_test = {
    "hemoglobin": 9.6,          # g/dL | Normal: M ≥13.5, F ≥12.0 | High risk: <10.0
    "wbc": 14800,               # /µL  | Normal: 4,000–11,000 | High: >11,000
    "platelets": 98000,         # /µL  | Normal: 150,000–450,000 | Low: <150,000
    "rbc": 3.2,                 # million/µL | Normal: M 4.7–6.1, F 4.2–5.4 | Low: below range
    "hematocrit": 29.4,         # %    | Normal: M 41–53, F 36–46 | Low: below range
    "mcv": 72,                  # fL   | Normal: 80–100 | Low (microcytosis): <80
    "mch": 23.1,                # pg   | Normal: 27–33 | Low: <27
    "mchc": 30.2,               # g/dL | Normal: 32–36 | Low: <32
    "rdw": 17.8,                # %    | Normal: 11.5–14.5 | High: >14.5
    "fasting_glucose": 168,     # mg/dL | Normal: 70–99 | High: ≥126
    "creatinine": 1.9,          # mg/dL | Normal: ≤1.3 | Clinically significant: ≥1.5
    "urea": 62,                 # mg/dL | Normal: 15–40 | High: >40
    "sodium": 128,              # mmol/L | Normal: 135–145 | Low: <135
    "potassium": 5.9            # mmol/L | Normal: 3.5–5.1 | High risk: >5.5
}




patient_3_normal_ecg = {
    "heart_rate": 72,           # bpm | Normal: 60–100 | Within normal limits
    "rhythm": "normal",         # Normal sinus rhythm | Any deviation considered abnormal
    "pr_interval": 160,         # ms  | Normal: 120–200 | Within normal limits
    "qrs_duration": 90,         # ms  | Normal: 80–120 | Within normal limits
    "qt_interval": 400,         # ms  | Normal: 350–450 | Within normal limits
    "st_segment": "isoelectric",# Should be isoelectric | Elevation or depression abnormal
    "t_wave": "upright",        # Upright in most leads | Inversion may indicate ischemia
    "p_wave": "normal",         # Present, upright, <120 ms | Absence or abnormal shape abnormal
    "axis": 60                  # degrees | Normal: -30 to +90 | Within normal limits
}


patient_3_abnormal_ecg = {
    "heart_rate": 120,          # bpm | Normal: 60–100 | High: >100 (tachycardia)
    "rhythm": "irregular",      # Normal sinus rhythm expected | Irregular → abnormal
    "pr_interval": 210,         # ms  | Normal: 120–200 | Prolonged → first-degree AV block
    "qrs_duration": 140,        # ms  | Normal: 80–120 | Wide QRS → bundle branch block
    "qt_interval": 480,         # ms  | Normal: 350–450 | Prolonged → arrhythmia risk
    "st_segment": "elevated",   # Should be isoelectric | Elevation → ischemia/infarct
    "t_wave": "inverted",       # Normal: upright | Inversion → ischemia / infarct
    "p_wave": "abnormal",       # Should be present, upright | Abnormal → conduction issue
    "axis": -45                  # degrees | Normal: -30 to +90 | Abnormal → axis deviation
}






surgery_counselling_data="""

---

**Package Details**

The following surgical packages are available:

**1) Basic Package  ₹15,000**
• Incision at 4 mm level
• Basic intraocular lens provided

**2) Standard Package  ₹45,000**
• Incision at 2 mm level (minimally invasive)
• Basic monofocal intraocular lens provided

**3) Advanced Package  ₹1,10,000**
• Incision at 2 mm level (minimally invasive)
• EDOF Toric intraocular lens provided
• Provides better vision at near, intermediate, and distance levels
• Reduces dependence on spectacles
• Corrects astigmatism

**4) Premium Package  ₹2,00,000**
• Incision at 2 mm level (minimally invasive)
• Premium multifocal toric intraocular lens provided
• Offers excellent near vision for reading and detailed work
• Provides maximum spectacle independence

---


**Surgery Method Details**

• Packages 1, 2, and 3 involve SICS-based surgery (performed using a surgical incision).
• Laser-assisted surgery is available at an additional cost of ₹45,000, over and above the selected package.

---

**Insurance Details**

1. Premium lenses (bifocal, trifocal, and multifocal) are **not covered** under insurance.

2. EDOF toric lenses may be covered by insurance **in select cases**, subject to approval by the insurance provider.
   • Usage must be medically justified and supported with proper documentation.

3. Laser-assisted surgery is covered by insurance **only for diabetic patients** with documented retinal complications.

4. In case of dual insurance policies:
   • One claim can be processed via the cashless method
   • The second claim must be processed through reimbursement
   • Both claims **cannot** be availed through the cashless method

5. Pre-operative investigations and post-operative medications are covered under insurance.

6. OPD charges will **not** be included in the surgical invoice for insurance claims.

---                      """