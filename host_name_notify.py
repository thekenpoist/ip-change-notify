from netmiko import ConnectHandler
import miniupnpc
import smtplib
import sys


class FirstLoco():

    
    def get_external_ip(): #queries the router for the external IP and returns that value

        home_ip = miniupnpc.UPnP()
        home_ip.discoverdelay = 100
        home_ip.discover()
        home_ip.selectigd()

        return home_ip.externalipaddress()


    def send_gmail(email,password,msg): #creates a gmail session and sends an email 
    
        smtp_object = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_object.ehlo()
        smtp_object.starttls()
        smtp_object.login(email,password)
        smtp_object.sendmail(email,email,msg)
        smtp_object.quit()


    def generate_message(file,new_ip):  #opens a file containing the email address and password
                                        #creates the message subject and body, and returns all three as as a list
        f = open(file)
        info = f.readlines()
        f.close()

        subject = 'Your IP has changed'
        msg = "Subject: "+subject+'\n'+new_ip

        return info[0],info[1],msg


    def compare_ip(file):   #compare the old IP stored in a file to the queried IP from the router 
                            #if different, overwrite the IP file and return both IP's as a list
        f = open(file, 'r')
        old_ip = f.read()
        f.close()

        new_ip = FirstLoco.get_external_ip()

        if old_ip == new_ip:
            sys.exit()
        else:
            f = open(file, 'w')
            f.write(new_ip)
            f.close()
            
            return old_ip.rstrip(), new_ip


    def update_ip_ssh_config(old_ip, new_ip, hostip, usernm, passwd, local_path, global_path): #updates the IP on the remote box
        linux_connect = ConnectHandler(
            device_type="linux",
            host=hostip,
            username=usernm,
            password=passwd
        )

        if global_path == '':
            linux_connect.send_command('sed -i ' + "'s/" + old_ip + '/' + new_ip + "/g' " + local_path)
        
        elif local_path == '':
            linux_connect.send_command('echo ' + passwd + ' | sudo -S sed -i ' + "'s/" + old_ip + '/' + new_ip + "/g' " + global_path)

        else:
            linux_connect.send_command('sed -i ' + "'s/" + old_ip + '/' + new_ip + "/g' " + local_path)
            linux_connect.send_command('echo ' + passwd + ' | sudo -S sed -i ' + "'s/" + old_ip + '/' + new_ip + "/g' " + global_path)

   
    def main():

        host_ip = '192.168.68.79'               #host where jhosts or .ssh/config file needs to be changed
        usernm = 'sifu'                         #username
        passwd = 'K3np0R0ck5'                   #user password
        local_path = '/home/sifu/config.txt'    #.ssh/config path - typically this is in the home dir
        global_path = ''                        #global path - typically this is /etc/hosts
        oldnew_ip = FirstLoco.compare_ip('IPaddress.txt')
        gm = FirstLoco.generate_message('emailpass.txt', oldnew_ip[1])
        FirstLoco.update_ip_ssh_config(oldnew_ip[0],oldnew_ip[1], host_ip, usernm, passwd, local_path, global_path)
        FirstLoco.send_gmail(gm[0],gm[1],gm[2])



FirstLoco.main()
