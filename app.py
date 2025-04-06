import requests
import json
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CCC_NUMS = {"2":"Evergreen Valley College","3":"Los Angeles City College","4":"College of Marin","5":"College of San Mateo","6":"College of the Sequoias","8":"Butte College","9":"Cerro Coso Community College","10":"Columbia College","13":"Merritt College","14":"Rancho Santiago College","16":"Cuesta College","17":"Merced College","18":"Las Positas College","20":"Barstow Community College","25":"Los Angeles Trade Technical College","27":"American River College","28":"Contra Costa College","30":"College of the Desert","31":"Los Angeles Harbor College","32":"Mission College","33":"City College of San Francisco","35":"Fresno City College","36":"Kings River College","38":"Shasta College","40":"Lake Tahoe Community College","41":"Cabrillo College","43":"Glendale Community College","44":"Los Angeles Valley College","45":"San Diego Miramar College","47":"Los Angeles Mission College","48":"Ohlone College","49":"Pasadena City College","51":"Foothill College","52":"Modesto Junior College","53":"Mt. San Jacinto College","54":"San Diego City College","55":"Golden West College","56":"Palomar College","57":"Santa Rosa Junior College","58":"Vista Community College","61":"Los Medanos College","62":"Mount San Antonio College","63":"Palo Verde College","64":"Rio Hondo College","65":"Saddleback College","66":"Santiago Canyon College","67":"West Hills College Coalinga","68":"Canada College","69":"Chaffey College","70":"Crafton Hills College","71":"Cypress College","72":"Gavilan College","73":"Napa Valley College","74":"Orange Coast College","77":"Laney College","78":"Riverside City College","80":"West Valley College","82":"Lassen Community College","83":"College of the Redwoods","84":"Bakersfield College","86":"Los Angeles Pierce College","87":"Oxnard College","90":"Yuba College","91":"West Los Angeles College","92":"Santa Barbara City College","93":"Sierra College","94":"Solano Community College","95":"Ventura College","96":"Chabot College","97":"Citrus College","99":"Cuyamaca College","100":"Mendocino College","101":"San Diego Mesa College","102":"College of the Siskiyous","103":"El Camino College","104":"Cerritos College","105":"Coastline Community College","106":"Grossmont College","107":"Imperial Valley College","108":"MiraCosta College","109":"San Joaquin Delta College","110":"Allan Hancock College","111":"College of Alameda","112":"Copper Mountain College","113":"De Anza College","114":"Diablo Valley College","118":"East Los Angeles College","119":"Taft College","121":"Antelope Valley College","122":"Feather River College","123":"Hartnell College","124":"Irvine Valley College","125":"Porterville College","126":"Sacramento City College","127":"Skyline College","130":"Los Angeles Southwest College","131":"San Bernardino Valley College","133":"Monterey Peninsula College","134":"Fullerton College","135":"Long Beach City College","136":"San Jose City College","137":"Santa Monica College","138":"Southwestern College","139":"Moorpark College","140":"College of the Canyons","142":"Cosumnes River College","145":"Folsom Lake College","146":"West Hills College Lemoore","147":"Woodland Community College","148":"Norco College","149":"Moreno Valley College","150":"Clovis Community College","153":"Compton College","200":"Madera Community College"}
CCC_NUMS = {int(k): v for k, v in CCC_NUMS.items()}

# UC_NUMS = {79: "UC Berkeley", 89: "UC Davis", 120: "UC Irvine", 117: "UC Los Angeles", 144: "UC Merced", 46: "UC Riverside", 7: "UC San Diego", 128: "UC Santa Barbara", 132: "UC Santa Cruz"}
UC_NUMS = {"UC Berkeley": 79, "UC Davis": 89, "UC Irvine": 120, "UC Los Angeles": 117, "UC Merced": 144, "UC Riverside": 46, "UC San Diego": 7, "UC Santa Barbara": 128, "UC Santa Cruz": 132}
uc_codes = {"ucb": "UC Berkeley", "ucd": "UC Davis", "uci": "UC Irvine", "ucla": "UC Los Angeles", "ucm": "UC Merced", "ucr": "UC Riverside", "ucsd": "UC San Diego", "ucsb": "UC Santa Barbara", "ucsc": "UC Santa Cruz"}

IVC_NUM = 124

payload = ""
headers = {
    "cookie": "ARRAffinity=19020555a6ce13e7884acd0cd2d8a32f62deb6e74d19a876d58f79edefb7bfc8; ARRAffinitySameSite=19020555a6ce13e7884acd0cd2d8a32f62deb6e74d19a876d58f79edefb7bfc8",
    "User-Agent": "insomnia/10.1.1"
}

# @app.route("/")
def get_ivc_courses(key):
    
    ivc_url = f"https://assist.org/api/articulation/Agreements?Key={key}"
    # basic url example  = "https://assist.org/api/institutions/124/agreements"

    response = requests.request("GET", ivc_url, data=payload, headers=headers)

    # All json data
    base_json = response.json()
    articulation_json = base_json.get("result").get("articulations")
    articulation_json = json.loads(articulation_json)

    ivc_articulations = {} # key = UC/CSU course : value = IVC course

    for key in articulation_json:
        # All data for each course 
        all_course_data = key.get("articulation")
        # UC/CSU course json catagory
        info_type = all_course_data.get("type")
        # UC/CSU major course 
        if info_type == "Course":
            course = all_course_data.get("course")
            four_year_course = f"{course.get('prefix')} {course.get('courseNumber')}: {course.get('courseTitle')}"
        else:
            try:
                info_type = info_type.lower()
                course = all_course_data.get(info_type)
                four_year_course = course.get("name")
            except:
                print(info_type)
                print(course)
                print(type(all_course_data), type(course))
                print(all_course_data)
                raise TypeError("Error: invalid info type")
            
        
        # IVC course json catagory
        sending_articulation = all_course_data.get("sendingArticulation")
        ivc_course = sending_articulation.get("items")
        # Check if IVC course exists (may not when explainer text is provided)
        if ivc_course:
            # returns as list
            ivc_course = ivc_course[0]
            ivc_course_list = ivc_course.get("items")
            size = len(ivc_course_list)
            ivc_course = ivc_course_list[0]
            return_ivc_course = f"{ivc_course.get('prefix')} {ivc_course.get('courseNumber')}: {ivc_course.get('courseTitle')}"
            if size > 1:
                for i in range(1, size):
                    ivc_course = ivc_course_list[i]
                    return_ivc_course += f" AND {ivc_course.get('prefix')} {ivc_course.get('courseNumber')}: {ivc_course.get('courseTitle')}"
            # Add to dict of ivc articulations
            ivc_articulations[four_year_course] = return_ivc_course
        
    return ivc_articulations

@app.route("/ccc_nums")
def get_ccc_nums():
    """
    Needed to make ccc_nums list. Not needed to be called in final app. 
    """
    ccc_nums = {}

    for ccc_num in range(1, 202):
        ccc_url = f"https://assist.org/api/articulation/Agreements?Key=75/{ccc_num}/to/89/Major/510d5fe2-4f0f-40e7-135c-08dcbcdb53de"
        response = requests.request("GET", ccc_url, data=payload, headers=headers)

        # All json data
        base_json = response.json()
        if base_json.get("isSuccessful") == False:
            continue
        # CCC info
        college_info_json = base_json.get("result").get("sendingInstitution")
        college_info_json = json.loads(college_info_json)

        print(college_info_json["code"], college_info_json["names"][0].get("name"), college_info_json["category"])

        is_ccc = college_info_json["isCommunityCollege"]
        if not is_ccc:
            continue
        else:
            ccc_nums[int(college_info_json["id"])] = college_info_json["names"][0].get("name")
        
    return jsonify(ccc_nums)


def get_outside_courses(ivc_articulations, major_key):
    ccc_articulations = {} # key = UC/CSU course : value = CCC course

    for ccc_num in CCC_NUMS:
        # remove for full app
        # if ccc_num > 30:
        #     break
        ccc_key = major_key.replace(f"{IVC_NUM}", f"{ccc_num}")
        ccc_url = f"https://assist.org/api/articulation/Agreements?Key={ccc_key}"
        response = requests.request("GET", ccc_url, data=payload, headers=headers)

        # All json data
        base_json = response.json()
        articulation_json = base_json.get("result").get("articulations")
        articulation_json = json.loads(articulation_json)


        for key in articulation_json:
           # All data for each course 
            all_course_data = key.get("articulation")
            # UC/CSU course json catagory
            info_type = all_course_data.get("type")
            # UC/CSU major course 
            if info_type == "Course":
                course = all_course_data.get("course")
                four_year_course = f"{course.get('prefix')} {course.get('courseNumber')}: {course.get('courseTitle')}"
            else:
                try:
                    info_type = info_type.lower()
                    course = all_course_data.get(info_type)
                    four_year_course = course.get("name")
                except:
                    print(type(all_course_data), type(course))
                    print(all_course_data)
                    raise TypeError("Error: invalid info type")

            # Check if UC/CSU equivalent course is not offered at IVC
            if four_year_course not in ivc_articulations.keys():
                # CCC course json catagory
                sending_articulation = all_course_data.get("sendingArticulation")
                ccc_course = sending_articulation.get("items")
                # Check if CCC course exists (may not when explainer text is provided)
                if ccc_course:
                    # returns as list
                    ccc_course = ccc_course[0]
                    ccc_course_list = ccc_course.get("items")
                    size = len(ccc_course_list)
                    ccc_course = ccc_course_list[0]
                    ccc_course_return = f"{ccc_course.get('prefix')} {ccc_course.get('courseNumber')}: {ccc_course.get('courseTitle')}"
                    if size > 1:
                        for i in range(1, size):
                            ccc_course = ccc_course_list[i]
                            ccc_course_return += f" AND {ccc_course.get('prefix')} {ccc_course.get('courseNumber')}: {ccc_course.get('courseTitle')}"
                    ccc_course_return = {ccc_course_return: CCC_NUMS[ccc_num]}

                    # Add to dict of ccc articulations
                    if four_year_course not in ccc_articulations.keys():
                        ccc_articulations[four_year_course] = [ccc_course_return]
                    else:
                        if ccc_course_return not in ccc_articulations[four_year_course]:
                            ccc_articulations[four_year_course].append(ccc_course_return)
    return ccc_articulations


@app.route("/majors")
def get_major(uc_num):
    majors_url = f"https://assist.org/api/agreements?receivingInstitutionId={uc_num}&sendingInstitutionId={IVC_NUM}&academicYearId=75&categoryCode=major"
    response = requests.request("GET", majors_url, data=payload, headers=headers)

     # All json data
    base_json = response.json()
    majors_json = base_json.get("reports")
    majors = {major.get("label"): major.get("key") for major in majors_json}
    return majors


def select_uc():
    """
    Pick UC to transfer to. Runs in terminal. Needs to be converted to website. 
    """
    while True:
        uc_name = input("Where do you want to transfer?: ").strip()
        if uc_name.lower() in uc_codes.keys():
            uc_name = uc_codes[uc_name]
            break
        else:
            print(f"{uc_name} is not a valid UC code. Try UCLA, UCI, UCSC, etc.")
    
    return uc_name

def select_major(all_majors):
    """
    Pick your UC major. Runs in terminal. Needs to be converted to website.
    """
    majors = list(all_majors.keys())
    for i, major in enumerate(majors):
        print(f"{i + 1}: {major}")
    
    while True:
        major = input("Select Major Number: ")
        try:
            major_index = int(major)
            if major_index <= 0:
                print(f"{major} is not a valid major number. Try an integer between 1 and {len(majors)}.")
                continue
            major_index = major_index - 1
            return majors[major_index]
        except ValueError:
            print(f"{major} is not a valid major number. Try an integer between 1 and {len(majors)}.")

def display_ivc_courses(ivc_articulations):
    """
    Display IVC articulations. Runs in terminal. Needs to be converted to website.
    """
    print(f"Articulated courses at IVC:")
    for course in ivc_articulations:
        print(f"\t{course} <- {ivc_articulations[course]}")
    print("Searching for different articulations at other community colleges... ")

def display_search_results(other_articulations):
    """
    Display other community colleges articulations. Runs in terminal. Needs to be converted to website.
    """ 
    print("Search Complete!")
    if other_articulations:
        print("Other UC equivalencies found:")
        for course in other_articulations:
            print(f"\t{course}")
            for equivalent in other_articulations[course]:
                ccc_course = list(equivalent.keys())[0]
                print(f"\t\t{ccc_course} @ {equivalent[ccc_course]}")
    else:
        print("No other courses found.")

@app.route("/search", methods=["GET", "POST"])
def search():
    print(request.form)
    major = request.form.get("major_select")
    all_majors = data_store[0]
    key = all_majors[major]
    uc_name = data_store[1]

    # print(key, type(key))
    ivc_articulations = get_ivc_courses(key)
    # return jsonify(ivc_articulations)
    display_ivc_courses(ivc_articulations)
    other_articulations = get_outside_courses(ivc_articulations, key)
    display_search_results(other_articulations)
    return render_template("other_courses.html", result=other_articulations, ivc_courses=ivc_articulations, uc_name=uc_name, major=major)

data_store = []

@app.route("/", methods=["GET", "POST"])
def main():
    # uc_name = select_uc()
    # uc_num = UC_NUMS[uc_name]
    # all_majors = get_major(uc_num)
    # major = select_major(all_majors)
    # print(f"\nSelected: {major}")
    print(request, request.method)
    if request.method == "POST":
        uc_name = request.form.get("uc_name")
        uc_num = UC_NUMS[uc_name]
        all_majors = get_major(uc_num)
        data_store.append(all_majors)
        data_store.append(uc_name)
        return render_template("major_list.html", all_majors=all_majors, uc_name=uc_name)
    else:
        return render_template("table(1).html")
    
   
