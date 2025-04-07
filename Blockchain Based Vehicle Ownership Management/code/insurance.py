from flask import *
from database import *
from blk import *

insurance = Blueprint('insurance', __name__)

@insurance.route('/insurance_home')
def insurance_home():
    return render_template('insurance_home.html')

@insurance.route('/insurance_view_policy_request', methods=['GET', 'POST'])
def insurance_view_policy_request():
    data = {}
    s = """
        SELECT pr.policyrequest_id, pr.policy_id, pr.allotvehicle_id, pr.policynumber, pr.date, pr.status, av.chasisnumber, av.modelnumber, p.policydetails
        FROM policyrequest pr
        INNER JOIN allotvehicle av ON pr.allotvehicle_id = av.allotvehicle_id
        INNER JOIN policy p ON pr.policy_id = p.policy_id
        WHERE p.insurance_id='%s'
    """ % (session['iid'])
    data['requests'] = select(s)
    
    if request.method == 'POST':
        action = request.form['action']
        request_id = request.form['request_id']
        if action == 'accept':
            u = "UPDATE policyrequest SET status='Accepted' WHERE policyrequest_id='%s'" % (request_id)
            
            qrty="select * from policyrequest where policyrequest_id='%s'" % (request_id)
            ress=select(qrty)
            policy_id=ress[0]['policy_id']
            allotvehicle_id=ress[0]['allotvehicle_id']
            policynumber=ress[0]['policynumber']
            
            
            import datetime
            d = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(compiled_contract_path) as file:
                contract_json = json.load(file)  # Load contract info as JSON
                contract_abi = contract_json['abi']  # Fetch contract's ABI - necessary to call its functions
            contract = web3.eth.contract(address=deployed_contract_address, abi=contract_abi)
            id = web3.eth.get_block_number()
            message = contract.functions.add_policyrequest(int(request_id),
                int(policy_id),
                int(allotvehicle_id),
                policynumber,
                d,
                'accept'
                
            ).transact({"from":web3.eth.accounts[0]})
        
        elif action == 'reject':
            u = "UPDATE policyrequest SET status='Rejected' WHERE policyrequest_id='%s'" % (request_id)
        update(u)
        return redirect(url_for('insurance.insurance_view_policy_request'))
    
    return render_template('insurance_view_policy_request.html', data=data)

@insurance.route('/insurance_manage_policy',methods=['get','post'])
def insurance_manage_policy():
    data={}
    s="select * from policy where insurance_id='%s'"%(session['iid'])
    data['value']=select(s)
    
    if 'submit' in request.form:
        pd=request.form['pd']
        details=request.form['details']
        a="insert into policy values(null,'%s','%s','%s',curdate())"%(session['iid'],pd,details)
        insert(a)
        return redirect(url_for('insurance.insurance_manage_policy'))
    
    if 'action' in request.args:
        action=request.args['action']
        id=request.args['id']
    else:
        action=None
    if action=='delete':
        b="delete from policy where policy_id='%s'"%(id)
        delete(b)
        return redirect(url_for('insurance.insurance_manage_policy'))
    if action=='update':
        n="select * from policy where policy_id='%s'"%(id)
        data['up']=select(n)
    if 'update' in request.form:
        pd=request.form['pd']
        details=request.form['details']
        u="update policy set policydetails='%s',details='%s' where policy_id='%s'"%(pd,details,id)
        update(u)
        return redirect(url_for('insurance.insurance_manage_policy'))
    return render_template('insurance_manage_policy.html',data=data)