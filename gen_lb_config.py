import sys
from mako.template import Template
import ConfigParser
import socket

### Static Variables ###
KEEP_ALIVE_PORT = "8080"
KEEP_ALIVE_TYPE = "http"
KEEP_ALIVE_URI = "/JsSf3LoWJn8aM3sWQ2LBsx4mM6/index.jsp"
SERVICE_PROTOCOL = "tcp"
STICKY_INACT_TIMEOUT = "480"
OWNER_PORT = "443"
OWNER_PROTOCOL = "tcp"
REDIRECT_PORT = "80"
REDIRECT_PROTOCOL = "tcp"

class IP:
	"""IP Class"""

	def __init__(self, addr):
		# Validate IP Address
		try:
			socket.inet_aton(addr)
			self.addr = addr
		except socket.error:
			raise ValueError("IP '%s' not valid" % addr)
	
	def __str__(self):
		return self.addr
	
	def octet(self):
		"""return the address splited"""
		return self.addr.split(".")
			

class CiscoCSS:

	def __init__(self,configFile):
		self.config = ConfigParser.ConfigParser()
		self.config.read(configFile)

		# Validate all config keys
		try:
			self.vip_ip = IP(self.config.get("Global","vip_ip"))
			self.redirect_url = self.config.get("Global","redirect_url")
			self.env = self.config.get("Global","env")
			self.app_name = self.config.get("Global","app_name")
			self.service_ip = [IP(addr.strip()) for addr in self.config.get("Global","service_ip").split(",")]

			self.template_keepalive = self.config.get("Template","template_keepalive")
			self.template_service = self.config.get("Template","template_service")
			self.template_group = self.config.get("Template","template_group")
			self.template_owner = self.config.get("Template","template_owner")
		except ConfigParser.NoOptionError, err:
			raise ValueError(err)
		except ConfigParser.NoSectionError, err:
			raise ValueError(err)
	
	def printConfig(self):
		"""debug only"""
		print "vip_ip = ",self.vip_ip
		print "redirect_url = ",self.redirect_url
		print "env =",self.env 
		print "app_name =",self.app_name
		print "service_ip =",self.service_ip

	def getKeepAlive(self,index):
		template = Template(filename=self.template_keepalive)

		return template.render(ip_last_octet=self.service_ip[index].octet()[3],
        	                env=self.env,
        	                order=index+1,
        	                appname=self.app_name,
       	                	ip=self.service_ip[index],
        	                ka_port=KEEP_ALIVE_PORT,
        	                ka_type=KEEP_ALIVE_TYPE,
        	                ka_uri=KEEP_ALIVE_URI)

	def getService(self,index):
		template = Template(filename=self.template_service)
		return template.render(ip_last_octet=self.service_ip[index].octet()[3],
			env=self.env,
       	                order=index+1,
       	                appname=self.app_name,
       	                ip=self.service_ip[index],
			svc_proto=SERVICE_PROTOCOL)

	def getGroup(self):
		template = Template(filename=self.template_group)
		return template.render(ip_last_octet=self.vip_ip.octet()[3],
			env=self.env,
       	                appname=self.app_name,
       	                ip=self.vip_ip,
       	                service_ip_1="%s_%s1_ka_%s" % (self.service_ip[0].octet()[3],self.env,self.app_name),
       	                service_ip_2="%s_%s2_ka_%s" % (self.service_ip[1].octet()[3],self.env,self.app_name),
			)

	def getOwner(self):
		template = Template(filename=self.template_owner)
		return template.render(vip_last_octet=self.vip_ip.octet()[3],
			env=self.env,
       	                app_name=self.app_name,
       	                vip_ip=self.vip_ip,
       	                service_1="%s_%s1_ka_%s" % (self.service_ip[0].octet()[3],self.env,self.app_name),
       	                service_2="%s_%s2_ka_%s" % (self.service_ip[1].octet()[3],self.env,self.app_name),
			redirect_url=self.redirect_url,
			STICKY_INACT_TIMEOUT=STICKY_INACT_TIMEOUT,
			OWNER_PORT=OWNER_PORT,
			OWNER_PROTOCOL=OWNER_PROTOCOL,
			REDIRECT_PORT=REDIRECT_PORT,
			REDIRECT_PROTOCOL=REDIRECT_PROTOCOL,
			)

		
	def printAll(self):

		for i in range(len(self.service_ip)):
			print self.getKeepAlive(i)
			print self.getService(i)

		print self.getGroup()
		print self.getOwner()




if __name__ == "__main__":

	if len(sys.argv) != 2:
		print("\n")
		print("ERROR: You should enter input file path!!!\n")
		print("USAGE: %s <config_file>\n" % sys.argv[0])
		sys.exit(100)

	try:
		cisco = CiscoCSS(sys.argv[1])
	except ValueError,err:
		print err
		sys.exit(200)
	
	cisco.printAll()


sys.exit(1)
