# gNMI Python Client

## Installation

### Python 3

#### General Use

```commandline
...
```

#### Development

```bash
git clone https://github.com/mathershifter/gnmi-py.git
# installs pipenv and requirements
make init
pipenv shell
```

### Python 2

Not supported :)


### Usage

```
%  gnmip -h
usage: gnmip [-h] [--version] [--pretty] [--tls-ca TLS_CA] [--tls-cert TLS_CERT] [--tls-key TLS_KEY] [--tls-get-target-certificates] [--insecure] [--host-override HOST_OVERRIDE] [--debug-grpc] [-u USERNAME]
             [-p PASSWORD] [--encoding {json,bytes,proto,ascii,json-ietf}] [--prefix PREFIX] [--get-type {all,config,state,operational}] [--interval INTERVAL] [--heartbeat HEARTBEAT] [--aggregate]
             [--suppress] [--mode {stream,once,poll}] [--submode {target-defined,on-change,sample}] [--qos QOS]
             target {capabilities,get,subscribe} [paths ...]

positional arguments:
  target                gNMI gRPC server
  {capabilities,get,subscribe}
                        gNMI operation [capabilities, get, subscribe]

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --pretty              pretty print notifications
  --tls-ca TLS_CA       certificate authority
  --tls-cert TLS_CERT   client certificate
  --tls-key TLS_KEY     client key
  --tls-get-target-certificates
                        retrieve certificates from the target
  --insecure            disable TLS
  --host-override HOST_OVERRIDE
                        Override gRPC server hostname

gRPC options:
  --debug-grpc          enable gRPC debugging

metadata:
  -u, --username USERNAME
  -p, --password PASSWORD

Common options:
  --encoding {json,bytes,proto,ascii,json-ietf}
                        set encoding
  --prefix PREFIX       gRPC path prefix (default: <empty>)

Get options:
  --get-type {all,config,state,operational}
  paths

Subscribe options:
  --interval INTERVAL   sample interval in milliseconds (default: 10s)
  --heartbeat HEARTBEAT
                        heartbeat interval in milliseconds (default: None)
  --aggregate           allow aggregation
  --suppress            suppress redundant
  --mode {stream,once,poll}
                        Specify subscription mode
  --submode {target-defined,on-change,sample}
                        subscription sub-mode
  --qos QOS             DSCP value to be set on transmitted telemetry
```


### Examples


#### Command-line

```bash
gnmip --insecure --user admin localhost:50051 subscribe /interfaces

# using jq to filter results
gnmip --insecure --user admin localhost:50051 subscribe /system | \
  jq '{time: .time, path: (.prefix + .updates[].path), value: .updates[].value}'
```


## API

```python
...
```
