#import libraries
import numpy as np
from flask import Flask, request, jsonify, render_template, send_from_directory, url_for
import pickle
import pandas as pd
import joblib
import os
import google.generativeai as genai
import cv2
import math
import time
import cvzone
from cvzone.ColorModule import ColorFinder
from pitch import pitch
from batsman import batsman_detect
from ball_detect import ball_detect
from werkzeug.utils import secure_filename
import ffmpeg
import deliveries as py
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import flask
import torch
from collections import deque
from ultralytics import YOLO
import time
import subprocess


pd.DataFrame.iteritems = pd.DataFrame.items


###### Initialize the Flask app
app = Flask(__name__,  static_folder='static')

########## Initialize the dash app 
app_dash = dash.Dash(__name__, external_stylesheets=[dbc.themes.PULSE], meta_tags=[{'name': 'viewport', 'content': "width=device-width, initial-scale=1"}], server=app, url_base_pathname='/pathname/')
app_dash.title = "IPL Analytics"


#################################################################################### LOAD WIN PREDICTOR MODEL ####################################################################################
#ml_model = joblib.load('model.pkl')



#################################################################################### LOAD THE YOLO MODEL ####################################################################################
yolo_model_path = 'best.pt'
yolo_model = YOLO(yolo_model_path)

########### The functions for ball tracking
def angle_between_lines(m1, m2=1):
    if m1 != -1/m2:
        angle = math.degrees(math.atan(abs((m2 - m1) / (1 + m1 * m2))))
        return angle
    else:
        return 90.0


class FixedSizeQueue:
    def __init__(self, max_size):
        self.queue = deque(maxlen=max_size)
    
    def add(self, item):
        self.queue.append(item)
    
    def pop(self):
        self.queue.popleft()
        
    def clear(self):
        self.queue.clear()

    def get_queue(self):
        return self.queue
    
    def __len__(self):
        return len(self.queue)













######################################################################### Define and Config Video upload and Save folder for ball tracker #########################################################
TRACKER_UPLOAD_FOLDER = "static/uploads_tracker"
TRACKER_SAVE_FOLDER = "static/results_tracker"
os.makedirs(TRACKER_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TRACKER_SAVE_FOLDER, exist_ok=True)

app.config['TRACKER_UPLOAD_FOLDER'] = TRACKER_UPLOAD_FOLDER
app.config['TRACKER_SAVE_FOLDER'] = TRACKER_SAVE_FOLDER






######################################################################### Define and Config Video upload and Save folder for LBW detector ####################################################################
UPLOAD_FOLDER = 'static/uploads'
PROCESSED_FOLDER = 'static/processed_videos'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER






########################################################################################## GEMINI API #################################################################################
genai.configure(api_key="AIzaSyALSQg60p7vqNBdn5SHpFKhu0AE8lpe1cE")
# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 64,
  "max_output_tokens": 8192,
  "response_mime_type": "text/plain",
}
safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE",
  },
]


chat_session = None







################################################################################################ LBW Code  ####################################################################################

def analyze_lbw(video_path, output_path):
    # Initialize ColorFinder and HSV values for ball detection
    mycolorFinder = ColorFinder(False)
    hsvVals = {
        "hmin": 10, "smin": 44, "vmin": 192,
        "hmax": 125, "smax": 114, "vmax": 255,
    }

    # Tuned RGB color range for batsman detection
    tuned_rgb_lower = np.array([112, 0, 181])
    tuned_rgb_upper = np.array([255, 255, 255])

    # Tuned Canny thresholds for batsman detection
    tuned_canny_threshold1 = 100
    tuned_canny_threshold2 = 200

    cap = cv2.VideoCapture(video_path)

    # Get video properties
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    def ball_pitch_pad(x, x_prev, prev_x_diff, y, y_prev, prev_y_diff, batLeg):
        if x_prev == 0 and y_prev == 0:
            return "Motion", 0, 0

        if abs(x - x_prev) > 3 * abs(prev_x_diff) and abs(prev_x_diff) > 0:
            if y < batLeg:
                return "Pad", x - x_prev, y - y_prev

        if y - y_prev < 0 and prev_y_diff > 0:
            if y < batLeg:
                return "Pad", x - x_prev, y - y_prev
            else:
                return "Pitch", x - x_prev, y - y_prev

        return "Motion", x - x_prev, y - y_prev

    x, y, batLeg = 0, 0, 0
    x_prev, y_prev, prev_x_diff, prev_y_diff = 0, 0, 0, 0
    lbw_detected = False

    while True:
        x_prev, y_prev = x, y
        frame, img = cap.read()

        if not frame:
            break

        ballImg, pitchImg, batsmanImg = img.copy(), img.copy(), img.copy()
        ballContour, x, y = ball_detect(img, mycolorFinder, hsvVals)
        all_img = ballContour.copy() if ballContour is not None else img.copy()
        batsmanContours = batsman_detect(img, tuned_rgb_lower, tuned_rgb_upper, tuned_canny_threshold1, tuned_canny_threshold2)
        pitchContour = pitch(img)

        for cnt in pitchContour:
            if cv2.contourArea(cnt) > 50000:
                cv2.drawContours(pitchImg, cnt, -1, (0, 255, 0), 10)
                if all_img is not None:
                    cv2.drawContours(all_img, cnt, -1, (0, 255, 0), 10)

        current_batLeg = 10000
        for cnt in batsmanContours:
            if cv2.contourArea(cnt) > 5000:
                if min(cnt[:, :, 1]) < y and y != 0:
                    batLeg_candidate = max(cnt[:, :, 1])
                    if batLeg_candidate < current_batLeg:
                        current_batLeg = batLeg_candidate
                    cv2.drawContours(batsmanImg, cnt, -1, (0, 0, 255), 10)
                    if all_img is not None:
                        cv2.drawContours(all_img, cnt, -1, (0, 0, 255), 10)

        batLeg = current_batLeg
        motion_type, prev_x_diff, prev_y_diff = ball_pitch_pad(x, x_prev, prev_x_diff, y, y_prev, prev_y_diff, batLeg)

        if motion_type == "Pad":
            lbw_detected = True

        imgStackList = [
            ballContour if ballContour is not None else img,
            pitchImg, batsmanImg, all_img if all_img is not None else img
        ]
        imgStack = cvzone.stackImages(imgStackList, 2, 0.5)

        out.write(imgStack)  # Save processed frame
        #cv2.imshow("stack", imgStack)

        if cv2.waitKey(1) == ord("k"):
            while cv2.waitKey(1) != ord("k"):
                pass
        elif cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    out.release()
    #cv2.destroyAllWindows()

    result = "Potential LBW Detected!" if lbw_detected else "No LBW Detected (based on Pad condition)."
    print("Remember to tune batsman detection RGB values in batsman.py for better accuracy.")
    return result








################################################################################### Playing XI Prediction Code ###################################################################################
Team_1=  []
Team_2 = []
Team1_Squad = {}
Team2_Squad = {}

# Importing basic libraries
# Reading files
byb=pd.read_csv('IPl Ball-by-Ball 2008-2023.csv')
match= pd.read_csv('IPL Mathces 2008-2023.csv')
byb.head()

# Fantasy Points

Batsman_points = {'Run':1, 'bFour':1, 'bSix':2, '30Runs':4,
        'Half_century':8, 'Century':16, 'Duck':-2, '170sr':6,
                 '150sr':4, '130sr':2, '70sr':-2, '60sr':-4, '50sr':-6}

Bowling_points = {'Wicket':25, 'LBW_Bowled':8, '3W':4, '4W':8, 
                  '5W':16, 'Maiden':12, '5rpo':6, '6rpo':4, '7rpo':2, '10rpo':-2,
                 '11rpo':-4, '12rpo':-6}

Fielding_points = {'Catch':8, '3Cath':4, 'Stumping':12, 'RunOutD':12,
                  'RunOutInd':6}

# Storing team players
# Here I have to do manual work... choosing the players after the toss and putting them here

#TEAM 1
srh = ['Abdul Samad','HC Brook','AK Markram','H Klaasen','RA Tripathi',
              'B Kumar', 'T Natarajan','Washington Sundar','M Jansen','Kartik Tyagi','Umran Malik']

srh_fp = { 'HC Brook': 111, 'Adil Rashid': 111, 'H Klaasen':111 , 'B Kumar':111 , 'Abdul Samad':111, 'Abhishek Sharma':111 , 'AK Markram':111 , 'Fazalhaq Farooqi':111,
              'M Jansen': 111,'RA Tripathi' :111 , 'Kartik Tyagi':111 , 'T Natarajan': 111,'Umran Malik':111 ,
              'Washington Sundar':111 , 'M Markande': 111, 'Vivrant Sharma':111 , 'Samarth Vyas':111 , 'Sanvir Singh': 111,'Upendra Yadav':111 , 'Mayank Dagar':111 ,}

#TEAM 2
pbks = ['S Dhawan', 'MA Agarwal', 'Arshdeep Singh','LS Livingstone','K Rabada','Jitesh Sharma',
          'SM Curran','Bhanuka Rajapakse','RD Chahar','Harpreet Brar', 'M Shahrukh Khan']

pbks_fp = { 'S Dhawan':111,'MA Agarwal':111, 'M Shahrukh Khan':111 , 'RD Chahar':111, 'Arshdeep Singh': 111, 'Harpreet Brar':111, 'RA Bawa':111, 
            'Prabhsimran Singh':111 , 'R Dhawan': 111, 'Jitesh Sharma':111 , 
           'Baltej Singh Dhanda':111 , 'Atharva Taide':111 , 'LS Livingstone':111 , 'K Rabada':111 , 'JM Bairstow': 111,
            'NT Ellis':111,   'Bhanuka Rajapakse': 111, 'Shivam Singh': 111, 'Mohit Rathee': 111, 'Vidwath Kaverappa': 111, 'R Bhatia':111, 'Sikandar Raza': 111, 'SM Curran':111 ,}

#TEAM 3
csk = ['MS Dhoni', 'Matheesha Pathirana', 'Shivam Dube','RD Gaikwad','AT Rayudu', 'MM Ali' ,'RA Jadeja','AM Rahane','Devon Conway', 'DL Chahar','MJ Santner']

csk_fp = {'MS Dhoni':111, 'Devon Conway':111,'RD Gaikwad':111,'AT Rayudu':111,'Shivam Dube':111, 
          'MM Ali':111,'RA Jadeja':111,'Simarjeet Singh':111,'Subhranshu Senapati':111,'Matheesha Pathirana':111,
          'TU Deshpande':111,'Bhagath Varma':111,'Ajay Mandal':111,'KA Jamieson':111,'Nishant Sindhu':111,
          'Shaik Rasheed':111, 'BA Stokes':111, 'AM Rahane':111,'DL Chahar':111,'D Pretorius':111,'M Theekshana':111,'MJ Santner':111,
          'Mukesh Choudhary' : 111,  'PH Solanki':111, 'RS Hangargekar':111, }

#TEAM 4
kkr = ['N Rana','AD Russell', 'UT Yadav', 'SP Narine','Rahmanullah Gurbaz', 
       'SN Thakur', 'RK Singh', 'LH Ferguson', 'KL Nagarkoti','VR Iyer', 'Varun Chakravarthy']

kkr_fp = {'N Rana':326, 'AD Russell':545, 'SP Narine':172, 'Shakib Al Hasan':120, 'LH Ferguson':0,
               'KL Nagarkoti':-2, 'Harshit Rana':111 , 'Rahmanullah Gurbaz':111 , 'RK Singh':111 , 'SN Thakur':111 ,
              'TG Southee':111 , 'UT Yadav':111 , 'Varun Chakravarthy':111 , 'VR Iyer':111 , 'Mandeep Singh':111 ,'Liton Das':111 , 'K Khejroliya':111 , 'David Wiese':111 , 
              'Suyash Sharma':111 , 'VG Arora':111 ,'N Jagadeesan':111 ,'Anukul Roy':111,}

#TEAM 5
dc = ['DA Warner', 'A Nortje','AR Patel', 'C Sakariya', 'KL Nagarkoti', 'Kuldeep Yadav', 'Lalit Yadav', 'L Ngidi', 'MR Marsh', 'Mustafizur Rahman','PP Shaw']

dc_fp = {'Aman Khan':111,'DA Warner':111, 'A Nortje':111,'AR Patel':111, 'C Sakariya':111, 'KL Nagarkoti': 111, 'Kuldeep Yadav':111,
             'Lalit Yadav': 111, 'L Ngidi':111, 'MR Marsh':111, 'Mustafizur Rahman':111, 'P Dubey':111, 
             'PP Shaw':111, 'Ripal Patel':111,'R Powell':111,'Sarfaraz Khan':111,'KK Ahmed':111,'Vicky Ostwal':111,'YV Dhull':111,
             'RR Rossouw':111,'MK Pandey':111,'Mukesh Kumar':111,'I Sharma':111,'PD Salt':111,}

#TEAM 6
rcb= ['V Kohli' , 'GJ Maxwell' ,  'Mohammed Siraj',  'JR Hazlewood' ,'RM Patidar' , 'Anuj Rawat' , 'Shahbaz Ahmed',  'KD Karthik' ,'KV Sharma' , 'Wanindu Hasaranga' ,  'HV Patel' ]

rcb_fp = { 'V Kohli':414, 'GJ Maxwell':392, 'Shahbaz Ahmed':194, 'Faf Duplesis':350,
               'DT Christian':47, 'HV Patel':634, 'Mohammed Siraj':275, 'Akash Deep':111 , 'Anuj Rawat':111 , 'DJ Willey':111 ,
               'KD Karthik':111 , 'FA Allen':111 , 'JR Hazlewood':111 , 'KV Sharma':111 , 'MK Lomror':111 , 'RM Patidar':111 , 'S Kaul':111 ,
               'SS Prabhudessai':111 , 'Wanindu Hasaranga':111 , 'Sonu Yadav':111 , 'Avinash Singh':111 , 'Rajan Kumar':111 , 'Manoj Bhandage':111 ,
               'Will Jacks':111 , 'Himanshu Sharma':111 , 'RJW Topley':111 , }
               
#TEAM 7
mi = [ 'Ishan Kishan' , 'RG Sharma' ,  'SA Yadav',  'JJ Bumrah' ,'Akash Madhwal' , 'Tilak Varma' ,  'C Green',  'TH David' ,'PP Chawla' , 'K Kartikeya' , 'JP Behrendorff']

mi_fp = { 'Ishan Kishan':134,'RG Sharma':393,'SA Yadav':307, 
              'JJ Bumrah':382, 'Akash Madhwal':111 , 'Arjun Tendulkar':111 , 'D Brevis':111 ,
              'HR Shokeen':111 ,'JP Behrendorff':111 , 'JC Archer':111 , 'K Kartikeya':111 , 'Arshad Khan':111 , 'Tilak Varma':111,
              'Ramandeep Singh':111 , 'TH David':111 , 'T Stubbs':111 , 'R Goyal':111 , 'N Wadhera':111,
              'Shams Mulani':111 , 'Vishnu Vinod':111 , 'M Jansen':111 , 'PP Chawla':111 , 'JA Richardson':111 , 'C Green':111 , }

#TEAM 8
rr = ['SV Samson', 'JC Buttler', 'YBK Jaiswal', 'TA Boult', 'R Parag', 'SO Hetmyer', 'R Ashwin', 'M Prasidh Krishna', 'YS Chahal', 'D Padikkal', 'OC McCoy']

rr_fp = {'SV Samson':111 , 'JC Buttler':111 , 'D Padikkal':111 , 'Dhruv Jurel':111 , 'KC Cariappa':111 ,'Kuldeep Sen':111 , 'Kuldeep Yadav':111 ,
            'NA Saini':111 , 'OC McCoy':111 , 'M Prasidh Krishna':111 ,'R Ashwin':111 , 'R Parag':111 , 'SO Hetmyer':111 , 'TA Boult':111 , 
            'YBK Jaiswal':111 ,'YS Chahal':111 , 'Root':111 , 'Abdul P A':111 , 'Akash Vashisht':111 , 'M Ashwin':111 ,
            'KM Asif':111 , 'A Zampa':111 , 'Kunal Rathore':111 , 'Donovan Ferreira':111 , 'JO Holder':111 ,}

#TEAM 9
gt = [ 'HH Pandya', 'Rashid Khan', 'Shubman Gill', 'AS Joseph',  'R Tewatia','Mohammed Shami', 'WP Saha', 'Yash Dayal', 'DA Miller', 'B Sai Sudharsan','V Shankar']

gt_fp = {  'HH Pandya':111 , 'Rashid Khan':111 , 'Shubman Gill':111 , 'Abhinav Sadarangani':111 , 'AS Joseph':111 , 'B Sai Sudharsan':111 ,
             'DG Nalkande':111 , 'DA Miller':111 , 'J Yadav':111 , 'MS Wade':111 ,'Mohammed Shami':111 , 'Noor Ahmad':111 , 'PJ Sangwan':111 , 'R Sai Kishore':111 , 
             'R Tewatia':111 ,'V Shankar':111 , 'WP Saha':111 , 'Yash Dayal':111 , 'MM Sharma':111 , 'J Little':111 ,'Urvil Patel':111 , 'Shivam Mavi':111 , 
             'KS Bharat':111 , 'OF Smith':111 , 'KS Williamson':111 ,}

#TEAM 10

lsg = ['KL Rahul', 'KH Pandya', 'MP Stoinis', 'N Pooran', 'MA Wood',  'Q de Kock', 'Ravi Bishnoi' , 'Avesh Khan', 'A Badoni' , 'DJ Hooda', 'A Mishra' ]

lsg_fp = { 'KL Rahul':111 , 'Avesh Khan':111 , 'A Badoni':111, 'DJ Hooda':111 , 'K Gowtham':111, 'KS Sharma':111, 'KH Pandya':111 ,
               'KR Mayers':111,'M Vohra':111 , 'MP Stoinis':111 , 'MA Wood':111, 'Mayank Yadav':111 , 'Mohsin Khan':111, 'Q de Kock':111, 'Ravi Bishnoi':111 ,
               'Yudhvir Charak':111,'Naveen-ul-Haq':111 , 'Swapnil Singh':111 , 'PN Mankad':111, 'A Mishra':111 , 'Daniel Sams':111, 'R Shepherd':111, 'Yash Thakur':111 ,
               'JD Unadkatt':111,'N Pooran':111 , }


def get_players(team1,team2,team1_fp):
    fantasy_team_players = []

    for i in range(len(team1)):
        unq_ids = byb[byb["batsman"]==team1[i]]['id'].unique()
        mathces_played = len(unq_ids)
#         print ( "Number of matches played" , len(unq_ids),team1[i])
        bbr = []
        for x in unq_ids:
            bat_run = sum(byb[(byb["batsman"]==team1[i])&(byb['id']==x)]['batsman_runs'])
            bbr.append(bat_run)

        r30,r50,r100 =0,0,0
        for m in bbr:
            if m>=100:
                r100+=1
            elif m>=50:
                r50+=1
            elif m>=30:
                r30+=1
        try:
            catches = len(byb[(byb['fielder']==team1[i]) & (byb['dismissal_kind']=='caught')])/mathces_played
            run_outs = len(byb[(byb['fielder']==team1[i]) & (byb['dismissal_kind']=='run out')])/mathces_played
            extra_points = r30/mathces_played*Batsman_points['30Runs'] +r50/mathces_played*Batsman_points['Half_century'] +r100/mathces_played*Batsman_points['Century'] +catches*Fielding_points['Catch']+run_outs*Fielding_points['RunOutInd']
        except:
            catches, run_outs, extra_points = 0,0,0
        
        # Extra Points for bowlers to be estimated here
        wickets_taken = []
        for x in unq_ids:
            twx = sum(byb[(byb["bowler"]==team1[i]) & (byb['id']==x)]['is_wicket'])
            wickets_taken.append(twx)

        w3,w4,w5 = 0,0,0
        for z in wickets_taken:
            if z>=5:
                w5+=1
            elif z>=4:
                w4+=1
            elif z>=3:
                w3+=1
        try:
            lbws = len((byb[(byb['bowler']==team1[i]) & (byb['dismissal_kind']=='lbw')]))/mathces_played      
            bowled = len((byb[(byb['bowler']==team1[i]) & (byb['dismissal_kind']=='bowled')]))/mathces_played      
            wexp = w3/mathces_played*Bowling_points['3W'] + w4/mathces_played*Bowling_points['4W'] + w5/mathces_played*Bowling_points['5W'] + lbws*Bowling_points['LBW_Bowled'] + bowled*Bowling_points['LBW_Bowled']
        except:
            lbws, bowled, wexp = 0,0,0
        
        ffp = []
        for j in range(len(team2)):
            bat_vs_bowl = byb[(byb["batsman"]==team1[i]) & (byb["bowler"]==team2[j])]
            bowls_played = len(bat_vs_bowl.batsman_runs)
            runs_scored = sum(bat_vs_bowl.batsman_runs)
            fours = len(bat_vs_bowl[bat_vs_bowl['batsman_runs']==4])
            sixes = len(bat_vs_bowl[bat_vs_bowl['batsman_runs']==6])
            wicket = sum(bat_vs_bowl.is_wicket)
            if bowls_played <=6*10 and wicket >=5:
                penalty = -16
                print (team1[i], "ka wicket taken",wicket,"times by", team2[j])
            elif bowls_played <=6*8 and wicket >=4:
                penalty = -8
                print (team1[i], "ka wicket taken",wicket,"times by", team2[j])
            elif bowls_played <=6*6 and wicket >=3:
                penalty = -4
                print (team1[i], "'s wicket taken",wicket,"times by", team2[j])
            else:
                penalty = 0

            try:    
                strike_rate = int(runs_scored/bowls_played*100)
            except: 
                strike_rate = 'NA'            
            if bowls_played >=10 and strike_rate!='NA':
                if strike_rate >=170:
                    print (team1[i] ,"beaten", team2[j], "Runs", runs_scored,"bowls",bowls_played,"strike rate", strike_rate,'Out',wicket,'times', "Fours", fours,"Sixes", sixes)            
                elif strike_rate >=150:
                    print (team1[i] ,"beaten", team2[j], "Runs", runs_scored,"bowls",bowls_played,"strike rate", strike_rate,'Out',wicket,'times', "Fours", fours,"Sixes", sixes)            
   
            bowl_vs_bat = byb[(byb["bowler"]==team1[i]) & (byb["batsman"]==team2[j])]
            wicket_took = sum(bowl_vs_bat.is_wicket)
            fantasy_points1 = runs_scored + fours*Batsman_points['bFour'] + sixes*Batsman_points['bSix'] - wicket*Bowling_points['Wicket'] + wicket_took*Bowling_points['Wicket'] + penalty 
            ffp.append(fantasy_points1)
            print (team1[i] ,"against", team2[j], "Runs", runs_scored, 
                     "bowls",bowls_played,"strike rate", strike_rate,
                     'Out',wicket,'times', "Fours", fours,"Sixes", sixes, "fatansy points",fantasy_points1)
        sum_ffp = sum(ffp)
        if team1_fp[team1[i]] > 0:
            recent_performace_points = np.log(team1_fp[team1[i]])
        elif team1_fp[team1[i]] <0:
            recent_performace_points = -np.log(abs(team1_fp[team1[i]]))
        else:
            recent_performace_points = 0
        # Trying a new method for recent performancec point
        recent_performace_points = team1_fp[team1[i]]/3
        weight1 = 0.5
        weight2 = 1 - weight1
        final_fantasy_point = (sum_ffp + extra_points + wexp)*weight1 + recent_performace_points*weight2
        final_fantasy_point = round(final_fantasy_point,2)
        fantasy_team_players.append((final_fantasy_point,team1[i]))
        fantasy_team_players.sort(reverse=True)
#         print ("Fatasy points of",team1[i],final_fantasy_point)
    return fantasy_team_players




########################################################################## Define the landing page ######################################################################################
@app.route('/')
def landing():
    return render_template('1.landing.html')



########################################################################## Load the signup page ######################################################################################
@app.route('/signup',methods=['POST'])
def signup():
    if request.method == 'POST':
        return render_template('2.signup.html')


########################################################################## Load the signup success page after saving entered password, gmail, and username ####################################
@app.route('/signupsuccess',methods=['POST'])
def signupsuccess():
    if request.method == 'POST':
        credentials = [(x) for x in request.form.values()]
        print(credentials)
        username = credentials[0]
        gmail = credentials[1]
        password = credentials[2]
        print(type(username))

        file = open("Username/username.txt", "w")
        a = file.write(username)
        file.close()

        file = open("Gmail/gmail.txt", "w")
        a = file.write(gmail)
        file.close()

        file = open("Password/password.txt", "w")
        a = file.write(password)
        file.close()
        return render_template('3.signupsuccess.html')


########################################################################## Load home page from other pages ######################################################################################
@app.route('/home2',methods=['POST'])
def home2():
    if request.method == 'POST':
        return render_template('6.home.html')

########################################################################## Load home page from other pages ######################################################################################
@app.route('/home3')
def home3():
    return render_template('6.home.html')

########################################################################## Load the login page ######################################################################################
@app.route('/login',methods=['POST'])
def login():
    if request.method == 'POST':
        return render_template('4.login.html')


########################################################################## Load home page after checking entered password, gmail, and username #########################################
@app.route('/home',methods=['POST'])
def home():
    if request.method == 'POST':
        lcredentials = [(x) for x in request.form.values()]
        print(lcredentials)
        lusername = lcredentials[0]
        lgmail = lcredentials[1]
        lpassword = lcredentials[2]
        print(type(lusername))

        f = open("Username/username.txt", "r")
        username = f.read()
        f = open("Gmail/gmail.txt", "r")
        gmail = f.read()
        f = open("Password/password.txt", "r")
        password = f.read()
        print(lusername, username, lpassword, password)

        if username==lusername and password==lpassword and gmail==lgmail:
            print('match')
            template = '6.home.html'
        elif username!=lusername or password!=lpassword or gmail!=lgmail:
            print('No')
            template = '5.loginfailed.html'

        return render_template(template)



########################################################################## Load the about page ######################################################################################
@app.route('/about')
def about():
    return render_template('13.about.html')

########################################################################## Load the win predictor page ######################################################################################
@app.route('/winpredictor')
def winpredictor():
    return render_template('winpredict.html')

########################################################################## Load the landing page from other pages #########################################################################
@app.route('/landing2',methods=['POST'])
def landing2():
    if request.method == 'POST':
        return render_template('1.landing.html')


########################################################################## Load the win prediction result page after getting the result from the model ##############################################
def calculate_crr(target_runs, runs_left, balls_left):
    total_runs = target_runs - runs_left
    total_overs = balls_left / 6
    return total_runs / total_overs

def calculate_rrr(target_runs, runs_left, balls_left):
    remaining_runs = target_runs - runs_left
    remaining_overs = balls_left / 6
    return remaining_runs / remaining_overs


@app.route('/prediction_result',methods=['POST'])
def prediction_result():
    if request.method == 'POST':
        input_data = [(x) for x in request.form.values()]
        print(input_data)
        batting_team = input_data[0]
        bowling_team = input_data[1]
        city = input_data[2]
        runs_left = float(input_data[3])
        balls_left = float(input_data[4])
        wickets_left = float(input_data[5])
        target = float(input_data[6])

        current_run_rate = calculate_crr(target,runs_left,balls_left)
        required_run_rate = calculate_rrr(target, runs_left,balls_left)

        # Create a DataFrame with the input values
        data = [[batting_team, bowling_team, city, runs_left, balls_left, wickets_left,
             current_run_rate, required_run_rate, target]]
        columns = ['BattingTeam', 'BowlingTeam', 'City', 'runs_left', 'balls_left',
               'wickets_left', 'current_run_rate', 'required_run_rate', 'target']
        input_df = pd.DataFrame(data, columns=columns)

        team1 = batting_team
        team2 = bowling_team

        # Make the prediction using the loaded model
        prediction = ml_model.predict_proba(input_df)
        #prediction = 'Yeah'
        print(prediction)


    return render_template('predictionresult.html', team1=team1, team2=team2, probability1=int(prediction[0, 0] * 100), probability2=int(prediction[0, 1] * 100))






########################################################################## Load the chatbot page and get input and display output ###########################################################
@app.route('/chatbot')
def chatbot():
    return render_template('16.chatbot.html')



# Route to handle chat messages
@app.route('/ask', methods=['POST'])
def ask_question():
    model = genai.GenerativeModel(
  model_name="gemini-1.5-flash-latest",
  safety_settings=safety_settings,
  generation_config=generation_config,
)
    global chat_session  # Use a global variable to maintain the session across requests

    user_message = request.form.get('question')

    # Initialize the chat session once for a continuous conversation
    if chat_session is None:
        chat_session = model.start_chat()

    try:
        # Send user message and get a response
        response = chat_session.send_message('Act as Cricket expert to answer to user questions and limit your answers simple and in 80 words maximum' + user_message)
        bot_reply = response.text
    except Exception as e:
        bot_reply = "I'm sorry, I couldn't get an answer for that question."

    return jsonify({'answer': bot_reply})




########################################################################## Load the video upload page for LBW #########################################################################
@app.route('/uploadvideo')
def uploadvideo():
    return render_template('uploadvideo.html')



########################################################################## Load the result page for LBW after generating the output ############################################################
@app.route("/lbw", methods=["POST"])
def lbw():
    if 'videoFile' not in request.files:
        return 'No file uploaded', 400

    file = request.files['videoFile']
    if file.filename == '':
        return 'No selected file', 400
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    output_filename = "processed.mp4"
    output_path = os.path.join(app.config['PROCESSED_FOLDER'], output_filename)

    # Run LBW detection
    result_message = analyze_lbw(file_path, output_path)


    # Convert video to H.264 (Main Profile)
    input_video = "static/processed_videos/processed.mp4"
    output_video = "static/processed_videos/processed_h264.mp4"
    try:
        ffmpeg.input(input_video).output(output_video, vcodec='libx264', preset='medium', crf=23).run(overwrite_output=True)
        print("[SUCCESS] Video converted to H.264 (Main Profile) and saved as:", output_video)
    except ffmpeg.Error as e:
        print("[ERROR] FFmpeg failed:", e.stderr.decode())

    return render_template('lbwresult.html', result=result_message, video_path=output_filename, video_url=url_for('static', filename='processed_videos/processed_h264.mp4'))
    



########################################################################## Load the playing X1 predictor input page #########################################################################
@app.route('/index', methods=['GET', 'POST'])
def index():
    
    global Team_1, Team_2, Team1_Squad, Team2_Squad,user_choice1,user_choice2
    if request.method == 'POST':
        if 'team1' in request.form:
            user_choice1 = request.form['team1']
    # rest of your code
        else:
    # handle the case where 'team1' is not present in the form
            error_message = 'Please select a team for Team 1.'
            print(error_message)
    
        if 'team2' in request.form:
            user_choice2 = request.form['team2']
    # rest of your code
        else:
    # handle the case where 'team1' is not present in the form
            error_message = 'Please select a team for Team 2.'
            print(error_message)

        p1 = 'Teams/' + user_choice1 + '.xlsx'
        p1_df = pd.read_excel(p1)
        players1 = p1_df['player_name'].tolist()
        print('Team 1 Players are: ', players1)

        p2 = 'Teams/' + user_choice2 + '.xlsx'
        p2_df = pd.read_excel(p2)
        players2 = p2_df['player_name'].tolist()
        print('Team 2 Players are: ', players2)

        if user_choice1 == 'srh':
            Team1_Squad = srh_fp
        elif user_choice1 == 'pbks':
            Team1_Squad = pbks_fp
        elif user_choice1 == 'csk':
            Team1_Squad = csk_fp
        elif user_choice1 == 'kkr':
            Team1_Squad = kkr_fp
        elif user_choice1 == 'dc':
            Team1_Squad = dc_fp
        elif user_choice1 == 'rcb':
            Team1_Squad = rcb_fp
        elif user_choice1 == 'mi':
            Team1_Squad = mi_fp
        elif user_choice1 == 'rr':
            Team1_Squad = rr_fp
        elif user_choice1 == 'gt':
            Team1_Squad = gt_fp
        elif user_choice1 == 'lsg':
            Team1_Squad = lsg_fp
        else:
            print("Invalid choice.")
        print('Thennnnn ', Team1_Squad)

        if user_choice2 == 'srh':
            Team2_Squad = srh_fp
        elif user_choice2 == 'pbks':
            Team2_Squad = pbks_fp
        elif user_choice2 == 'csk':
            Team2_Squad = csk_fp
        elif user_choice2 == 'kkr':
            Team2_Squad = kkr_fp
        elif user_choice2 == 'dc':
            Team2_Squad = dc_fp
        elif user_choice2 == 'rcb':
            Team2_Squad = rcb_fp
        elif user_choice2 == 'mi':
            Team2_Squad = mi_fp
        elif user_choice2 == 'rr':
            Team2_Squad = rr_fp
        elif user_choice2 == 'gt':
            Team2_Squad = gt_fp
        elif user_choice2 == 'lsg':
            Team2_Squad = lsg_fp
        else:
            print("Invalid choice.")
        print('Thennnnn ', Team2_Squad)

        selected_players1 = request.form.getlist('player1')
        selected_players2 = request.form.getlist('player2')
        print(selected_players1)
        print(selected_players2)

        if len(selected_players1) == 11 and len(selected_players2) == 11:
            Team_1 = selected_players1
            Team_2 = selected_players2
              
        else:
            error_message = 'Please select exactly 11 players for both teams.'
            return render_template('player.html', players1=players1, players2=players2, error_message=error_message)

        t1 = get_players(Team_1, Team_2, Team1_Squad)
        t2 = get_players(Team_2, Team_1, Team2_Squad)

        t3 = t1 + t2
        t3.sort(reverse=True)
        Team = pd.DataFrame(t3)
        Result = Team[1].head(11)
        Result = pd.DataFrame(Result)
        print('\nFinal Predicted Team',Result)

        predicted_team = Result.to_html()  # Convert the result to HTML

        return render_template('result.html', predicted_team=predicted_team)

    return render_template('index.html')






################################################################################  Dash Board Code  ##########################################################################################
@app.route('/plotly_dashboard') 
def render_dashboard():
    return flask.redirect('/pathname')

batsman_names = py.balls.batsman.sort_values().unique()
bowler_names = py.balls.bowler.sort_values().unique()

batsman_types_of_graph = {
    'Runs per season': py.plot_batsman_runs,
    'Distribution of runs': py.distribution_of_runs,
    'Favorite venues': py.fav_venues,
    'Favorite bowlers': py.fav_bowlers,
    'Runs against teams': py.most_runs_against_team,
    'Runs by over': py.runs_by_over,
}

bowler_types_of_graph = {
    'Runs conceded per season': py.plot_bowler_runs,
    'Economy rate by season': py.plot_economy_rate,
    'Wickets by season': py.wicket_data,
    'Wickets by over': py.wickets_by_over,
    'No. of wickets by player': py.most_wickets_against
}

vs_types_of_graph = {
    'Strike rate': py.strike_rate_batsman_bowler,
    'Distribution of wickets': py.wickets_batsman_bowler
}

navbar = dbc.NavbarSimple(
    
    brand='Analytics Dashboard',
    color='primary',
    dark=True,
    fluid=True,
    sticky='top'
)

header = dbc.Row([
    dbc.Col([
        html.H2('Indian Premier League'),
        html.P('''
        The Indian Premier League is a professional Twenty20 cricket league in India contested during March or April and 
        May of every year by eight teams representing eight different cities in India.
        '''),
        dbc.Button("Teams playing", id='teams-playing', className='mb-2'),
    ], width=6),

    dbc.Col([
        html.H2('Analytics Dashboard'),
        html.P('''
        An interactive analytics dashboard for IPL which contains data from all seasons till 2019. 
        '''),
        html.P('''
        You can analyze runs scored, dismissals, strike rates by player, toss statistics and other insights. 
        I'm working on adding additional insights. If you have any ideas, drop me a message.'''),
        dbc.Collapse(
            dbc.ListGroup(
                [
                    dbc.ListGroupItem('Chennai Super Kings'),
                    dbc.ListGroupItem('Mumbai Indians'),
                    dbc.ListGroupItem('Kolkata Knight Riders'),
                    dbc.ListGroupItem('Royal Challengers Bangalore'),
                    dbc.ListGroupItem('Kings XI Punjab'),
                    dbc.ListGroupItem('Sunrisers Hyderabad'),
                    dbc.ListGroupItem('Rajasthan Royals'),
                    dbc.ListGroupItem('Delhi Capitals'),
                ]
            ),
            id='collapse'
        )
    ], width=6),
], className='mt-4')

batsman_section = dbc.Card(
    dbc.CardBody([
        html.Label(
            "Graph",
            htmlFor='graph_type_bat'
        ),
        dcc.Dropdown(
            id='graph_type_bat',
            options=[{'label': i, 'value': i} for i in batsman_types_of_graph.keys()],
            placeholder='Select graph',
            value="Runs per season"
        ),

        html.Label(
            "Batsman",
            htmlFor='batsman_name'
        ),

        dcc.Dropdown(
            id='batsman_name',
            options=[{'label': x, 'value': x} for x in batsman_names],
            placeholder='Select batsman',
            value='V Kohli'
        ),

        dcc.Graph(
            id='graph_bat',
            className='graph_fill',
            config={
                'showTips': True,
                'displayModeBar': False
            }
        ),
    ])
)

bowler_section = dbc.Card(
    dbc.CardBody([
        html.Label(
            "Graph",
            htmlFor='graph_type_bowl'
        ),
        dcc.Dropdown(
            id='graph_type_bowl',
            options=[{'label': i, 'value': i} for i in bowler_types_of_graph.keys()],
            value='Runs conceded per season',
            placeholder='Select graph'
        ),
        html.Label(
            "Bowler",
            htmlFor='bowler_name'
        ),
        dcc.Dropdown(
            id='bowler_name',
            options=[{'label': x, 'value': x} for x in bowler_names],
            value='JJ Bumrah',
            placeholder='Select bowler'
        ),

        dcc.Graph(
            id='graph_bowl',
            className='graph_fill',
            config={
                'showTips': True,
                'displayModeBar': False
            },

        ),
    ])
)

player_v_player_section = dbc.Card([
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.Label(
                    "Graph",
                    htmlFor='graph_vs_type'
                ),
                dcc.Dropdown(
                    id='graph_vs_type',
                    options=[{'label': i, 'value': i} for i in vs_types_of_graph.keys()],
                    value='Strike rate',
                    placeholder='Select type of graph'
                ),
            ])
        ]),

        dbc.Row([
            dbc.Col([
                html.Label(
                    'Batsman',
                    htmlFor='batsman_vs'
                ),
                dcc.Dropdown(
                    id='batsman_vs',
                    options=[{'label': i, 'value': i} for i in batsman_names],
                    value='V Kohli',
                    placeholder='Select batsman',
                ),
            ], width=6),
            dbc.Col([
                html.Label(
                    'Bowler',
                    htmlFor='bowler_vs'
                ),
                dcc.Dropdown(
                    id='bowler_vs',
                    options=[{'label': i, 'value': i} for i in bowler_names],
                    value='Harbhajan Singh',
                    placeholder='Select bowler'
                ),
            ], width=6),
        ]),

        dcc.Graph(
            id='batsman_v_bowler',
            className='graph_fill',
            config={
                'showTips': True,
                'displayModeBar': False
            }
        )
    ])
])

toss_section = dbc.Card([
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.Span(children=[
                    html.H5('Toss Outcome'),
                    dbc.RadioItems(
                        id='toss_cond',
                        options=[
                            {'label': "Win", "value": 'win'},
                            {'label': "Lose", "value": 'lose'}
                        ],
                        value='win',
                        labelStyle={'display': 'inline-block'}
                    )
                ], style={'textAlign': 'center'}),
            ], width=6),

            dbc.Col(children=[
                html.Span(children=[
                    html.H5('Toss Decision'),
                    dbc.RadioItems(
                        id='toss_decision',
                        options=[
                            {'label': "Bat", "value": 'bat'},
                            {'label': "Field", "value": 'field'}
                        ],
                        value='bat',
                    )
                ], style={'textAlign': 'center'}),
            ], width=6),
        ]),

        dbc.Row(children=[
            dbc.Col([
                dcc.Graph(
                    id='toss_graph',
                    className='graph_fill',
                    config={
                        'showTips': True,
                        'displayModeBar': False
                    }
                )
            ])
        ])
    ])
])

tabs = dbc.Tabs(
    [
        dbc.Tab(batsman_section, label="Batsman", tab_id='batsman_tab', labelClassName='text-dark'),
        dbc.Tab(bowler_section, label="Bowler", tab_id='bowler_tab', labelClassName='text-dark'),
        dbc.Tab(player_v_player_section, label='Player vs. Player', tab_id='player_v_player_tab',
                labelClassName='text-dark'),
        dbc.Tab(toss_section, label='Toss Analysis', tab_id='toss_tab', labelClassName='text-dark')
    ],
    active_tab='batsman_tab',
    id='tabs')

body = dbc.Container(fluid=True, children=[
    header,
    dbc.Row([
        dbc.Col([
            tabs
        ])
    ], className='mt-4'),
])

app_dash.layout = html.Div(children=[navbar, body])


@app_dash.callback(
    Output(component_id='graph_bat', component_property='figure'),
    [Input(component_id='graph_type_bat', component_property='value'),
     Input(component_id='batsman_name', component_property='value'),
     Input('tabs', 'active_tab')]
)
def update_batsman_graph(type_graph, name, t):
    return batsman_types_of_graph[type_graph](name)


@app_dash.callback(
    Output(component_id='graph_bowl', component_property='figure'),
    [Input(component_id='graph_type_bowl', component_property='value'),
     Input(component_id='bowler_name', component_property='value'),
     Input('tabs', 'active_tab')]
)
def update_bowler_graph(type_graph, name, t):
    return bowler_types_of_graph[type_graph](name)


@app_dash.callback(
    Output(component_id='batsman_v_bowler', component_property='figure'),
    [Input(component_id='graph_vs_type', component_property='value'),
     Input(component_id='batsman_vs', component_property='value'),
     Input(component_id='bowler_vs', component_property='value'),
     Input('tabs', 'active_tab')]
)
def batsman_v_bowler_graph(type_graph, batsman_name, bowler_name, t):
    return vs_types_of_graph[type_graph](batsman_name, bowler_name)


@app_dash.callback(
    Output(component_id='toss_graph', component_property='figure'),
    [Input(component_id='toss_cond', component_property='value'),
     Input(component_id='toss_decision', component_property='value'),
     Input('tabs', 'active_tab')]
)
def update_toss_graph(toss_cond, toss_decision, t):
    return py.outcome_by_toss(toss_cond, toss_decision)


@app_dash.callback(
    Output('collapse', 'is_open'),
    [Input('teams-playing', 'n_clicks')],
    [State('collapse', 'is_open')]
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open





######################################################################################  Load the upload page for ball tracker   #####################################################################
@app.route('/uploadvideo2')
def uploadvideo2():
    return render_template('uploadvideo2.html')

######################################################################################  Load the result page for ball tracker   #####################################################################
@app.route("/ball_tracker", methods=["POST"])
def ball_tracker():
    if 'videoFile' not in request.files:
        return 'No file uploaded', 400  # Fix: Match the form field name

    file = request.files['videoFile']
    if file.filename == '':
        return 'No selected file', 400  # Fix: Properly handle empty upload
    
    file_path = os.path.join(TRACKER_UPLOAD_FOLDER, file.filename)
    fourcc = cv2.VideoWriter_fourcc(*'avc1')  # H.264 codec
    output_path = os.path.join(app.config['TRACKER_SAVE_FOLDER'], "tracked_video.mp4")
    #os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    
    cap = cv2.VideoCapture(file_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS), (int(cap.get(3)), int(cap.get(4))))
    


    ret = True
    prevTime = 0
    centroid_history = FixedSizeQueue(10)
    start_time = time.time()
    interval = 0.6
    paused = False
    angle = 0
    prev_frame_time = 0 
    new_frame_time = 0
    
    while ret:
        ret, frame = cap.read()
        if not ret:
            break
        
        results = yolo_model.track(frame, persist=True, conf=0.35, verbose=False)
        boxes = results[0].boxes.xyxy
        rows, cols = boxes.shape if len(boxes) > 0 else (0, 0)
        
        if len(boxes) != 0:
            for i in range(rows):
                x1, y1, x2, y2 = boxes[i]
                x1, y1, x2, y2 = x1.item(), y1.item(), x2.item(), y2.item()
                
                centroid_x = int((x1 + x2) / 2)
                centroid_y = int((y1 + y2) / 2)
                centroid_history.add((centroid_x, centroid_y))
                
                cv2.circle(frame, (centroid_x, centroid_y), radius=3, color=(0, 0, 255), thickness=-1)
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
        
        if len(centroid_history) > 1:
            centroid_list = list(centroid_history.get_queue())
            for i in range(1, len(centroid_history)):
                cv2.line(frame, centroid_history.get_queue()[i-1], centroid_history.get_queue()[i], (255, 0, 0), 4)


        if len(centroid_history) > 1:
            centroid_list = list(centroid_history.get_queue())
            x_diff = centroid_list[-1][0] - centroid_list[-2][0]
            y_diff = centroid_list[-1][1] - centroid_list[-2][1]
            if(x_diff!=0):
                m1 = y_diff/x_diff
                if m1==1:
                    angle = 90
                elif m1!=0:
                    angle = 90-angle_between_lines(m1)
                if angle>=45:
                        print("ball bounced")
            future_positions = [centroid_list[-1]]
            for i in range(1, 5):
                future_positions.append(
                    (
                        centroid_list[-1][0] + x_diff * i,
                        centroid_list[-1][1] + y_diff * i
                    )
                )
            print("Future Positions: ",future_positions)
            for i in range(1,len(future_positions)):
                cv2.line(frame, future_positions[i-1], future_positions[i], (0, 255, 0), 4)
                cv2.circle(frame,future_positions[i],radius=3,color=(0,0,255),thickness=-1)

        text = "Angle: {:.2f} degrees".format(angle)
        cv2.putText(frame,text,(20,20),cv2.FONT_HERSHEY_PLAIN,1,(255,0,0),2)
        
        out.write(frame)
    
    cap.release()
    out.release()


    input_video = "static/results_tracker/tracked_video.mp4"
    output_video = "static/results_tracker/tracked_video_h264.mp4"


    # Convert video to H.264 (Main Profile)
    try:
        ffmpeg.input(input_video).output(output_video, vcodec='libx264', preset='medium', crf=23).run(overwrite_output=True)
        print("[SUCCESS] Video converted to H.264 (Main Profile) and saved as:", output_video)
    except ffmpeg.Error as e:
        print("[ERROR] FFmpeg failed:", e.stderr.decode())






    print("Video URL:", url_for('static', filename='results_tracker/tracked_video_h264.mp4'))
    return render_template("trackerResult.html", video_url=url_for('static', filename='results_tracker/tracked_video_h264.mp4'))




################################################################################### Run the webapp ############################################################################################
if __name__ == "__main__":
    app.run(debug=True)

