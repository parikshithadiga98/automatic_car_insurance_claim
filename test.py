#!/usr/bin/env python
# coding: utf-8

# In[1]:


from flask import Flask,render_template,redirect, url_for,request,flash,session
import pymysql
import flask_session
import io
from PIL import Image
from base64 import b64encode
import os


# In[2]:


db = pymysql.connect("localhost","root","","vehicaldb", autocommit=True )
app = Flask(__name__)
app.config['SECRET_KEY'] = 'oh_so_secret'


# In[3]:


conn = db.cursor()


# In[4]:


@app.route('/')
def index():
    return  render_template("index.html")


# In[5]:


@app.route('/signup',methods=['POST','GET'])
def signup():
     if request.method == 'POST':
                name=request.form['uname']
                email=request.form['email']
                username=request.form['un']
                pas1=request.form['psw']
                pas2=request.form['psw1']
                if pas1==pas2:
                
                    sql=("""insert into custumer (cname, passwrd,username, email) VALUES (%s,%s,%s,%s)""",(name,pas1,username,email))
                    conn.execute(*sql)
                    return render_template("index.html")
                else:
                    error="please type same password"
        
                    return render_template("index.html",er=error)
            


# In[6]:


@app.route('/login',methods=['POST','GET'])
def login():
    error = None
    if request.method == 'POST':
        username=request.form['uname']
        psw=request.form['psw']
        sql=("""select username,passwrd,cid from custumer where username=%s and passwrd=%s""",(username,psw))
        conn.execute(*sql)
        try:
            
            un,psw,cid=conn.fetchone()
            session['username'],session['psw'],session['cid']=un,psw,cid
            print(session['cid'])
            if request.form['uname'] != un or request.form['psw'] != psw: 
                error="Invalid Credentials. Please try again."
                return render_template('index.html',error=error)
        
            else:
                sql=("""select cusid from images where cusid=%s""",(session.get('cid')))
                conn.execute(*sql)
                cid=conn.fetchone()
                if cid:
                    return redirect(url_for('down'))
                else:
                    return redirect(url_for('dash'))
        except:
            error="invalid username and password"
            return render_template('index.html',er=error)
            


# In[7]:


@app.route('/dash',methods=['POST','GET'])
def dash():
    return render_template("dash.html",welcome="Welcome "+session['username'])


# In[8]:


@app.route('/update',methods=['POST'])
def update():
    if request.method == 'POST':
                ccnum=request.form['vcn']
                rcnum=request.form['vrn']
                inum=request.form['in']
                finum=request.form['fir']
               # print(session.get('username'))
                sql1=("""select cusid from cvehicledetail  where cusid=%s""",(session.get('cid')))
                sql=("""insert into cvehicledetail (ccnum, rcnum,inum,cusid,firid) VALUES (%s,%s,%s,%s,%s)""",(ccnum,rcnum,inum,session.get('cid'),finum))
                conn.execute(*sql1)
                cid=conn.fetchone()
                print(cid)
                if cid:
                    si=("""delete from cvehicledetail where cusid=%s""",(session.get('cid')))
                    conn.execute(*si)
                #if (cid == session.get('cid')):
                    #sql3=("""update cvehicledetail set ccnum =%s,rcnum=%s,inum=%s where cusid=%s""",(ccnum,rcnum,inum,session.get('cid')))
                    #conn.execute(*sql3)
                #else:
                conn.execute(*sql)
                return redirect(url_for('down'))

               


# In[9]:


@app.route('/down')
def down():
    sql1=("""select ccnum,rcnum,inum,firid from cvehicledetail  where cusid=%s""",(session.get('cid')))
    conn.execute(*sql1)
    
    try:
        cc,vn,inum,fi=conn.fetchone()
    except:
    
        cc,vn,inum,fi='none','none','none','none'
    
    sql=("""select status,valueofdamage,damage from claim where cusid=%s""",(session.get('cid')))
    conn.execute(*sql)
    try:
        status,rms,damage=conn.fetchone()
    except:
    
        status,rms,damage='none','none','none'
    
     
    sql=("""select img1,img2,img3 from images where cusid=%s""",(session.get('cid')))
    conn.execute(*sql)
    img1,img2,img3=conn.fetchone()

   
    
    file1= b64encode(img1).decode("utf-8")
    file2= b64encode(img2).decode("utf-8")
    file3= b64encode(img3).decode("utf-8")
    
    
    
    return render_template("down.html",welcome="Welcome "+session['username'],cc=cc,vn=vn,pn=inum,fir=fi,i1=file1,i2=file2,i3=file3,status=status,rms=rms,damage=damage)
    
    
    
            


# In[ ]:





# In[10]:


@app.route('/cp',methods=['POST','GET'])
def cp():
    pas1=request.form['psw']
    pas2=request.form['psw1']
    if pas1==pas2:
        sql=("""update `custumer` set passwrd =%s where cid=%s""",(pas1,session.get('cid')))
        conn.execute(*sql)
        return redirect(url_for('down'))
    else:
         error="please type same password"
        
         return render_template("dash.html",er=error)
    
    


# In[11]:


@app.route('/upimg',methods=['POST','GET'])
def upimg():
    return redirect(url_for('dash'))
    


# In[12]:


@app.route('/upload',methods=['POST'])

def upload():
    #try:
    if request.method == 'POST':
        print(session.get('cid'))
        p1=request.files['up1']
        p2=request.files['up2']
        p3=request.files['up3']
        #print(p1.filepath)
        up1 = convertToBinaryData(p1.filename)
        up2 = convertToBinaryData(p2.filename)
        up3 = convertToBinaryData(p3.filename)
        sql=("""select cusid from images where cusid=%s""",(session.get('cid')))
        conn.execute(*sql)
        cid=conn.fetchone()
        if cid:
            si=("""delete from images where cusid=%s""",(session.get('cid')))
            conn.execute(*si)
        sql=("""insert into images (img1,img2,img3,cusid) values(%s,%s,%s,%s)""",(up1,up2,up3,session.get('cid')))
        conn.execute(*sql)
            
        return redirect(url_for('down'))
    #except:
        #return redirect(url_for('dash'))
        
def convertToBinaryData(filename):
    with open(filename, 'rb') as file:
        binaryData = file.read()
    return binaryData
                    
            
    


# In[13]:



@app.route('/claim',methods=['POST','GET'])
def claim():
    
    sql1=("""select cusid from claim  where cusid=%s""",(session.get('cid')))
    conn.execute(*sql1)
    delid=conn.fetchone()
    if delid:
        si=("""delete from claim where cusid=%s""",(session.get('cid')))
        conn.execute(*si)
        
    sql=("""select firid,rcnum from cvehicledetail  where cusid=%s""",(session.get('cid')))
    conn.execute(*sql)
    firn,vc=conn.fetchone()
    
    try:
        sql=("""select firnumber ,vcnum from policedata where vcnum=%s""",(vc))
        conn.execute(*sql)
        fir,vc=conn.fetchone()
        #print(firn)
        #print(fir)
    
        if(fir==firn):
            import detectionanddifferencecode as ddc
            rs,rms,damage=ddc.imgreading(session.get('cid'))
            print(damage)
            if rs=="not":
                label="claim not possible"
            else:
                label="claim possible"
            print(label)
            claimsql=("""insert into claim(cusid,status,valueofdamage,damage) values(%s,%s,%s,%s)""",(session.get('cid'),label,rms,damage))
            conn.execute(*claimsql)
        
            return redirect(url_for('down'))
        else:
            #label="ur waste"
            label="claim not possible"
            print(label)
            sql=("""insert into claim(cusid,status,valueofdamage,damage) values(%s,%s,%s,%s)""",(session.get('cid'),label,'0','no'))
            conn.execute(*sql)
            return redirect(url_for('down'))
    except:
        label="claim not possible"
        print(label)
        sql=("""insert into claim(cusid,status,valueofdamage,damage) values(%s,%s,%s,%s)""",(session.get('cid'),label,'1','no'))
        conn.execute(*sql)
        return redirect(url_for('down'))
    
    

    


# In[14]:


@app.route('/logout',methods=['POST','GET'])
def logout():
    if request.method == 'POST':
        if 'lout' in request.form:
                    session.pop('username', None)
                    session.pop('passwrd', None)
                    session.pop('cid', None)
                    return redirect(url_for('index'))
        


# In[15]:


@app.route('/delete',methods=['POST','GET'])
def delete():
    if request.method == 'POST':
        if 'del' in request.form:
            sql=("""DELETE FROM `custumer` where cid=%s""",(session['cid']))
            conn.execute(*sql)
            session.pop('username', None)
            session.pop('passwrd', None)
            session.pop('cid', None)
            return redirect(url_for('index'))


# In[ ]:


if __name__ == '__main__':
    app.run()


# In[ ]:




