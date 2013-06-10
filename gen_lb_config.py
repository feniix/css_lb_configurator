import sys
from mako.template import Template

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
    template = Template(filename='./templates/ecom/keepalive.tmpl')
    print(template.render(ip_last_octet=ip_last_octet,
                          env=env,
                          order=order,
                          appname=app_name,
                          ip=ip,
                          ka_port=KEEP_ALIVE_PORT,
                          ka_type=KEEP_ALIVE_TYPE,
                          ka_uri=KEEP_ALIVE_URI))


def print_service(ip_last_octet, ip, order, env, app_name, SERVICE_PROTOCOL):
    template = Template(filename='./templates/ecom/service.tmpl')
    print(template.render(ip_last_octet=ip_last_octet,
                          env=env,
                          order=order,
                          appname=app_name,
                          ip=ip,
                          svc_proto=SERVICE_PROTOCOL))


def print_group(vip_last_octet, env, app_name, vip, ip_last_octet_array,
                order_array):
    template = Template(filename='./templates/ecom/group.tmpl')
    print(template.render(ip_last_octet=vip_last_octet,
                          env=env,
                          appname=app_name,
                          ip=vip,))
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
        print('ERROR: File %s could not be opened!!!' % input_file)
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
