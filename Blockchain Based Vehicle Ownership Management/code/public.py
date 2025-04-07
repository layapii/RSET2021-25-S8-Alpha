from flask import *
from database import*
import uuid
from blk import *

public=Blueprint("public",__name__)
@public.route('/')
def index():
    return render_template('home.html')

@public.route('/login',methods=['get','post'])
def login():
    if 'login' in request.form:
        uname=request.form['uname']
        pwod=request.form['pwod']
        s="select * from login where username='%s' and password='%s'"%(uname,pwod)
        res=select(s)
        if res:
            session['lid']=res[0]['login_id']
            
            if res[0]['usertype']=='admin':
                return redirect(url_for('admin.admin_home'))
            elif res[0]['usertype']=='company':
                a="select * from company where login_id='%s'"%(session['lid'])
                res1=select(a)
                session['sid']=res1[0]['company_id']
                return redirect(url_for('company.company_home')) 
            elif res[0]['usertype']=='user':
                a="select * from user where login_id='%s'"%(session['lid'])
                res1=select(a)
                session['uid']=res1[0]['user_id']
                return redirect(url_for('user.user_home')) 
            
            elif res[0]['usertype']=='mvd':
                a="select * from mvd where login_id='%s'"%(session['lid'])
                res1=select(a)
                session['mid']=res1[0]['mvd_id']
                return redirect(url_for('mvd.mvd_home')) 
            # elif res[0]['usertype']=='bank':
            #     a="select * from bank where login_id='%s'"%(session['lid'])
            #     res1=select(a)
            #     session['bid']=res1[0]['bank_id']
            #     return redirect(url_for('bank.bank_home'))
            elif res[0]['usertype']=='insurance':
                a="select * from insurancecompany where login_id='%s'"%(session['lid'])
                res1=select(a)
                session['iid']=res1[0]['insurance_id']
                return redirect(url_for('insurance.insurance_home'))
    return render_template('login.html')

@public.route('/company_reg',methods=['get','post'])
def company_reg():
    if 'reg' in request.form:
        sname=request.form['sname']
        place=request.form['place']
        phone=request.form['phone']
        email=request.form['email']
        file=request.files['file']
        pht="static/"+str(uuid.uuid4())+file.filename
        file.save(pht)
        uname=request.form['uname']
        pawod=request.form['pawod']
        a="insert into login values(null,'%s','%s','pending')"%(uname,pawod)
        lid=insert(a)
        b="insert into company values(null,'%s','%s','%s','%s','%s','%s')"%(lid,sname,place,phone,email,pht)
        insert(b)
        return redirect(url_for('public.login'))
    return render_template('company_register.html')


@public.route('/user_registration', methods=['get', 'post'])
def user_registration():
    if 'register' in request.form:
        fname = request.form['fname']
        lname = request.form['lname']
        place = request.form['place']
        phone = request.form['phone']
        email = request.form['email']
        file=request.files['file']
        pht="static/"+str(uuid.uuid4())+file.filename
        file.save(pht)
        uname = request.form['uname']
        pawod = request.form['pawod']
        a = "insert into login values(null, '%s', '%s', 'pending')" % (uname, pawod)
        lid = insert(a)
        b = "insert into user values(null, '%s', '%s', '%s', '%s', '%s', '%s','%s')" % (lid, fname, lname, place, phone, email,pht)
        insert(b)
        
        # d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
        with open(compiled_contract_path) as file:
            contract_json = json.load(file)  # Load contract info as JSON
            contract_abi = contract_json['abi']  # Fetch contract's ABI - necessary to call its functions
        contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
        
        id = web3.eth.get_block_number()
        message = contract.functions.add_users(
            int(id),
            int(lid),
           
            fname,
            lname,
            place,
            phone,
            email,
            pht
            
        ).transact({"from":web3.eth.accounts[0]})
                
        
        
        return redirect(url_for('public.login'))
    return render_template('user_registration.html')




@public.route('/mvd_registration', methods=['get', 'post'])
def mvd_registration():
    if 'register' in request.form:
       
        lname = request.form['lname']
        place = request.form['place']
        phone = request.form['phone']
        email = request.form['email']
        # file=request.files['file']
        # pht="static/"+str(uuid.uuid4())+file.filename
        # file.save(pht)
        uname = request.form['uname']
        pawod = request.form['pawod']
        a = "insert into login values(null, '%s', '%s', 'mvd')" % (uname, pawod)
        lid = insert(a)
        b = "insert into mvd values(null, '%s', '%s', '%s', '%s', '%s')" % (lid, lname, place, phone, email)
        insert(b)
        return redirect(url_for('public.login'))
    return render_template('mvd_registration.html')






@public.route('/insurance_register', methods=['get', 'post'])
def insurance_register():
    if 'register' in request.form:
       
        lname = request.form['lname']
        place = request.form['place']
        phone = request.form['phone']
        email = request.form['email']
        file=request.files['file']
        pht="static/"+str(uuid.uuid4())+file.filename
        file.save(pht)
        uname = request.form['uname']
        pawod = request.form['pawod']
        a = "insert into login values(null, '%s', '%s', 'insurance')" % (uname, pawod)
        lid = insert(a)
        b = "insert into insurancecompany values(null, '%s', '%s', '%s', '%s', '%s','%s')" % (lid, lname, place, phone, email,pht)
        insert(b)
        return redirect(url_for('public.login'))
    return render_template('insurance_register.html')










@public.route('/bank_register', methods=['get', 'post'])
def bank_register():
    if 'register' in request.form:
       
        lname = request.form['lname']
        place = request.form['place']
        phone = request.form['phone']
        email = request.form['email']
        file=request.files['file']
        pht="static/"+str(uuid.uuid4())+file.filename
        file.save(pht)
        uname = request.form['uname']
        pawod = request.form['pawod']
        a = "insert into login values(null, '%s', '%s', 'bank')" % (uname, pawod)
        lid = insert(a)
        b = "insert into bank values(null, '%s', '%s', '%s', '%s', '%s','%s')" % (lid, lname, place, phone, email,pht)
        insert(b)
        return redirect(url_for('public.login'))
    return render_template('bank_register.html')