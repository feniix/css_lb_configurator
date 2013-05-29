import sys

### Static Variables ###
KEEP_ALIVE_PORT = "8080"
KEEP_ALIVE_TYPE = "http"
KEEP_ALIVE_URI = "/monitor/index.html"
SERVICE_PROTOCOL = "tcp"
STICKY_INACT_TIMEOUT = "480"
OWNER_PORT = "443"
OWNER_PROTOCOL = "tcp"
REDIRECT_PORT = "80"
REDIRECT_PROTOCOL = "tcp"

### Global Variables ###
input_file = ""
redirect_url = ""
vip = ""
vip_last_octet = ""
app_name = ""
env = ""
ip_array = []
ip_last_octet_array = []
order_array = []

### Functions definition ###

def print_keep_alive(ip_last_octet, ip, order, env, app_name, KEEP_ALIVE_PORT, 
                   KEEP_ALIVE_TYPE, KEEP_ALIVE_URI):
	print ('!************************* KEEPALIVE *************************')
	print ('keepalive ', ip_last_octet, '_', env, order, '_ka_', app_name, sep='')
	print ('  description \"keepalive for ', ip_last_octet, '_', env, order, 
	       '_', app_name, '\"', sep='')
	print ('  ip address ', ip, sep='')
	print ('  port ', KEEP_ALIVE_PORT, sep='')
	print ('  type ', KEEP_ALIVE_TYPE, sep='')
	print ('  uri \"', KEEP_ALIVE_URI, '\"', sep='')
	print ('  active\n')
	
def print_service(ip_last_octet, ip, order, env, app_name, SERVICE_PROTOCOL):
	print ('!************************** SERVICE **************************')
	print ('service ', ip_last_octet, '_', env, order, '_', app_name, sep='')
	print ('  ip address ', ip, sep='')
	print ('  keepalive type named ', ip_last_octet, '_', env, order, '_ka_',
	       app_name, sep='')
	print ('  protocol ', SERVICE_PROTOCOL, sep='')
	print ('  active\n')
	
def print_group(vip_last_octet, env, app_name, vip, ip_last_octet_array, order_array):
	print ('!*************************** GROUP ***************************')
	print ('group ', vip_last_octet, '_', env, '_', app_name, sep='')
	print ('  vip address ', vip, sep='')
	for i in range(len(order_array)):
		print ('  add destination service ', ip_last_octet_array[i], '_', env,
		       order_array[i], '_', app_name, sep='')
	print ('  active\n')
	
def print_owner(vip_last_octet, vip, env, app_name, ip_last_octet_array, order_array,
               STICKY_INACT_TIMEOUT, OWNER_PORT, OWNER_PROTOCOL,
			   REDIRECT_PORT, REDIRECT_PROTOCOL, redirect_url):
	print ('!*************************** OWNER ***************************')
	print ('owner ', vip_last_octet, '_', env, '_', app_name,'\n', sep='')
	print ('  content ', vip_last_octet, '_', env, '_', app_name, sep='')
	print ('    vip address ', vip, sep='')
	for i in range(len(order_array)):
		print ('    add service ', ip_last_octet_array[i], '_', env, order_array[i],
		       '_', app_name, sep='')
	print ('    add dns ', redirect_url, sep='')
	print ('    sticky-inact-timeout ', STICKY_INACT_TIMEOUT, sep='')
	print ('    port ', OWNER_PORT, sep='')
	print ('    protocol ', OWNER_PROTOCOL, sep='')
	print ('    advanced-balance sticky-srcip')
	print ('    active\n')
	print ('  content ', vip_last_octet, '_', env, '_', app_name, '_redir', sep='')
	print ('    vip address ', vip, sep='')
	print ('    sticky-inact-timeout ', STICKY_INACT_TIMEOUT, sep='')
	print ('    port ', REDIRECT_PORT, sep='')
	print ('    protocol ', REDIRECT_PROTOCOL, sep='')
	print ('    redirect \"https://', redirect_url, '\"', sep='')
	print ('    active\n')

	
### Script Main ###
	
if len(sys.argv) <= 1:
	print ("\n")
	print ("ERROR: You should enter input file path!!!\n")
	print ("USAGE: GenLBConfig.py <input_file_path>")
else:
	print ('\n')
	if (len(sys.argv)) == 2:
		input_file = str(sys.argv[1])
		
		# Parse input file
		try:
			input_fileContent = open(input_file)
			for line in input_fileContent:
				if (line.find("url") != -1):
					temp_array = line.split('=')
					redirect_url = (temp_array[len(temp_array)-1]).rstrip()
				if (line.find("vip") != -1):
					temp_array = line.split('=')
					vip = (temp_array[len(temp_array)-1]).rstrip()
				if (line.find("name") != -1):
					temp_array = line.split('=')
					app_name = (temp_array[len(temp_array)-1]).rstrip()
				if (line.find("env") != -1):
					temp_array = line.split('=')
					env = (temp_array[len(temp_array)-1]).rstrip()
				if (line.find("service_ip") != -1):
					temp_array = line.split('=')
					ip_array.append((temp_array[len(temp_array)-1]).rstrip())
			
			# Parse ips to retrieve the last octet
			temp_array = vip.split('.')
			vip_last_octet = temp_array[len(temp_array)-1]
			for i in range(len(ip_array)):
				temp_array = ip_array[i].split('.')
				ip_last_octet_array.append((temp_array[len(temp_array)-1]).rstrip())
				order_array.append(i+1)

			# Write LB configuration to standard output
			for i in range(len(ip_array)):
				print_keep_alive(ip_last_octet_array[i], ip_array[i], order_array[i],
							   env, app_name, KEEP_ALIVE_PORT, KEEP_ALIVE_TYPE,
							   KEEP_ALIVE_URI)
				print_service(ip_last_octet_array[i], ip_array[i], order_array[i],
							 env, app_name, SERVICE_PROTOCOL)
			print_group(vip_last_octet, env, app_name, vip, ip_last_octet_array, order_array)
			print_owner(vip_last_octet, vip, env, app_name, ip_last_octet_array, order_array,
					   STICKY_INACT_TIMEOUT, OWNER_PORT, OWNER_PROTOCOL,
					   REDIRECT_PORT, REDIRECT_PROTOCOL, redirect_url)
		except IOError:
			print ('ERROR: File \"', input_file, '\" could not be opened!!!', sep='')
			sys.exit()
		
	else:
		print ("ERROR: You should enter only one parameter!!! The input file path.\n")
		print ("USAGE: GenLBConfig.py <input_file_path>")
