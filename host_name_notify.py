from netmiko import ConnectHandler
import miniupnpc
import smtplib
import sys


class FirstLoco():

    
    def get_external_ip(self): #queries the router for the external IP and returns that value

        home_ip = miniupnpc.UPnP()
        home_ip.discoverdelay = 100
        home_ip.discover()
        home_ip.selectigd()

        return home_ip.externalipaddress()


    def send_gmail(self,email,password,msg): #creates a gmail session and sends an email 
    
        smtp_object = smtplib.SMTP('smtp.gmail.com', 587)
        smtp_object.ehlo()
        smtp_object.starttls()
        smtp_object.login(email,password)
        smtp_object.sendmail(email,email,msg)
        smtp_object.quit()


    def generate_message(self,file,new_ip):  #opens a file containing the email address and password
                                        #creates the message subject and body, and returns all three as as a list
        with open(file) as f:
            info = f.readlines()

        subject = 'Your IP has changed'
        msg = "Subject: "+subject+'\n'+new_ip

        return info[0],info[1],msg


    def compare_ip(self,file):   #compare the old IP stored in a file to the queried IP from the router 
                            #if different, overwrite the IP file and return both IP's as a list
        with open(file, 'r') as f:
            old_ip = f.read()

        new_ip = self.get_external_ip()

        if old_ip == new_ip:
            sys.exit()
        else:
            with open(file, 'w') as f:
                f.write(new_ip)
            
            return old_ip.rstrip(), new_ip


    def update_ip_ssh_config(self,old_ip, new_ip, hostip, usernm, passwd, local_path, global_path): #updates the IP on the remote box
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
        
    host_ip = '192.168.68.60'               #change this to the host where hosts or .ssh/config file needs to be changed
    usernm = 'frank'                        #change this to your username
    passwd = 'b00g3rs4b0und'                #change this to your user password
    local_path = '/home/frank/config.txt'   #if using local then change this to your .ssh/config path - typically this is in the home dir
    global_path = '/etc/hosts'              #if global then change this to your global path - typically this is /etc/hosts
    oldnew_ip = loco.compare_ip('/home/frank/ip-change-notify/IPaddress.txt') #change this to path/to/IPaddresss.txt file
    gm = loco.generate_message('/home/frank/ip-change-notify/emailpass.txt', oldnew_ip[1]) #change this to path/to/emailpass.txt
    loco.update_ip_ssh_config(oldnew_ip[0],oldnew_ip[1], host_ip, usernm, passwd, local_path, global_path)
    loco.send_gmail(gm[0],gm[1],gm[2])


loco = FirstLoco()
main()