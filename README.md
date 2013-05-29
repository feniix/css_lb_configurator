css_lb_configurator
===================

### Simple python script that helps create Cisco CSS 11500 load balancers

This script is being developed by Fernando Paci @ The Warranty Group

Requirements:

+ python 3 (currently working on migrating it to python 2.x)
+ file with the following structure:
```
url=dev.example.com
vip_ip=10.10.0.1
app_name=example
env=dev
service_ip_1=192.168.1.10
service_ip_2=192.168.1.11

```

Usage:

`python3 gen_lb_config.py dev.example.com`

Output:
```
!************************* KEEPALIVE *************************
keepalive 10_dev1_ka_example
  description "keepalive for 10_dev1_example"
  ip address 192.168.1.10
  port 8080
  type http
  uri "/monitor/index.html"
  active

!************************** SERVICE **************************
service 10_dev1_example
  ip address 192.168.1.10
  keepalive type named 10_dev1_ka_example
  protocol tcp
  active

!************************* KEEPALIVE *************************
keepalive 11_dev2_ka_example
  description "keepalive for 11_dev2_example"
  ip address 192.168.1.11
  port 8080
  type http
  uri "/monitor/index.html"
  active

!************************** SERVICE **************************
service 11_dev2_example
  ip address 192.168.1.11
  keepalive type named 11_dev2_ka_example
  protocol tcp
  active

!*************************** GROUP ***************************
group 1_dev_example
  vip address 10.10.0.1
  add destination service 10_dev1_example
  add destination service 11_dev2_example
  active

!*************************** OWNER ***************************
owner 1_dev_example

  content 1_dev_example
    vip address 10.10.0.1
    add service 10_dev1_example
    add service 11_dev2_example
    add dns dev.example.com
    sticky-inact-timeout 480
    port 443
    protocol tcp
    advanced-balance sticky-srcip
    active

  content 1_dev_example_redir
    vip address 10.10.0.1
    sticky-inact-timeout 480
    port 80
    protocol tcp
    redirect "https://dev.example.com"
    active

```
