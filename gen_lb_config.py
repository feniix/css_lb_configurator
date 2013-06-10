import sys

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
    print('!************************* KEEPALIVE *************************')
    print('keepalive {0}_{1}{2}_ka_{3}'.format(ip_last_octet, env, order,
          app_name))
    print('  description \"keepalive for {0}_{1}{2}_{3}\"'
          .format(ip_last_octet, env, order, app_name))
    print('  ip address {0}'.format(ip))
    print('  port {0}'.format(KEEP_ALIVE_PORT))
    print('  type {0}'.format(KEEP_ALIVE_TYPE))
    print('  uri \"{0}\"'.format(KEEP_ALIVE_URI))
    print('  active\n')


def print_service(ip_last_octet, ip, order, env, app_name, SERVICE_PROTOCOL):
    print('!************************** SERVICE **************************')
    print('service {0}_{1}{2}_{3}'.format(ip_last_octet, env, order, app_name))
    print('  ip address {0}'.format(ip))
    print('  keepalive type named {0}_{1}{2}_ka_{3}'
          .format(ip_last_octet, env, order, app_name))
    print('  protocol {0}'.format(SERVICE_PROTOCOL))
    print('  active\n')


def print_group(vip_last_octet, env, app_name, vip, ip_last_octet_array,
                order_array):
    print('!*************************** GROUP ***************************')
    print('group {0}_{1}_{2}'.format(vip_last_octet, env, app_name))
    print('  vip address {0}'.format(vip))
    for i in range(len(order_array)):
        print('  add destination service {0}_{1}{2}_{3}'
              .format(ip_last_octet_array[i], env, order_array[i], app_name))
    print('  active\n')


def print_owner(vip_last_octet, vip, env, app_name, ip_last_octet_array,
                order_array, STICKY_INACT_TIMEOUT, OWNER_PORT, OWNER_PROTOCOL,
                REDIRECT_PORT, REDIRECT_PROTOCOL, redirect_url):
    print('!*************************** OWNER ***************************')
    print('owner {0}_{1}_{2}\n'.format(vip_last_octet, env, app_name))
    print('  content {0}_{1}_{2}'.format(vip_last_octet, env, app_name))
    print('    vip address {0}'.format(vip))
    for i in range(len(order_array)):
        print('    add service {0}_{1}{2}_{3}'
              .format(ip_last_octet_array[i], env, order_array[i], app_name))
    print('    add dns {0}'.format(redirect_url))
    print('    sticky-inact-timeout {0}'.format(STICKY_INACT_TIMEOUT))
    print('    port {0}'.format(OWNER_PORT))
    print('    protocol {0}'.format(OWNER_PROTOCOL))
    print('    advanced-balance sticky-srcip')
    print('    active\n')
    print('  content {0}_{1}_{2}_redir'.format(vip_last_octet, env, app_name))
    print('    vip address {0}'.format(vip))
    print('    sticky-inact-timeout {0}'.format(STICKY_INACT_TIMEOUT))
    print('    port {0}'.format(REDIRECT_PORT))
    print('    protocol {0}'.format(REDIRECT_PROTOCOL))
    print('    redirect \"https://{0}\"'.format(redirect_url))
    print('    active\n')


def parse_input(input_file):
    global redirect_url
    global vip
    global vip_last_octet
    global app_name
    global env
    global ip_array
    global ip_last_octet_array
    global order_array

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
            ip_last_octet_array.\
                append((temp_array[len(temp_array)-1]).rstrip())
            order_array.append(i+1)
    except IOError:
        print('ERROR: File \"', input_file, '\" could not be opened!!!', '')
        sys.exit()

### Script Main ###
if len(sys.argv) <= 1:
    print("\n")
    print("ERROR: You should enter input file path!!!\n")
    print("USAGE: %s <input_file_path>" % __file__)
else:
    print('\n')
    if (len(sys.argv)) == 2:
        parse_input(str(sys.argv[1]))

        # Write LB configuration to standard output
        for i in range(len(ip_array)):
            print_keep_alive(ip_last_octet_array[i], ip_array[i],
                             order_array[i], env, app_name, KEEP_ALIVE_PORT,
                             KEEP_ALIVE_TYPE, KEEP_ALIVE_URI)
            print_service(ip_last_octet_array[i], ip_array[i], order_array[i],
                          env, app_name, SERVICE_PROTOCOL)

        print_group(vip_last_octet, env, app_name, vip, ip_last_octet_array,
                    order_array)

        print_owner(vip_last_octet, vip, env, app_name, ip_last_octet_array,
                    order_array, STICKY_INACT_TIMEOUT, OWNER_PORT,
                    OWNER_PROTOCOL, REDIRECT_PORT, REDIRECT_PROTOCOL,
                    redirect_url)

    else:
        print("ERROR: You should enter only one parameter!!! <input file>.\n")
        print("USAGE: %s <input_file_path>" % __file__)
