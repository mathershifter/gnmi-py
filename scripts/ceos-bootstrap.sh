#!/bin/sh

CEOS_IMAGE=${CEOS_IMAGE:-"ceoslab:4.34.1F"}
CEOS_CONTAINER=${CEOS_CONTAINER:-"ceoslab-gnmipy"}

mkdir -p "$(pwd)/.ceos/$CEOS_CONTAINER/flash"

echo "DISABLE=True" > "$(pwd)/.ceos/$CEOS_CONTAINER/flash/zerotouch-config"

docker rm -f "$CEOS_CONTAINER" 2> /dev/null || echo "container not found, ignoring..."

docker create --rm \
  --name="$CEOS_CONTAINER" \
  --privileged \
  -e CEOS=1 \
  -e EOS_PLATFORM=ceoslab \
  -e container=docker \
  -e ETBA=1 \
  -e SKIP_ZEROTOUCH_BARRIER_IN_SYSDBINIT=1 \
  -e INTFTYPE=eth \
  -e MAPETH0=1 \
  -e MGMT_INTF=eth0 \
  -p 50051:6030 \
  -v "$(pwd)/.ceos/$CEOS_CONTAINER/flash:/mnt/flash" \
  -it \
  "$CEOS_IMAGE" \
  /sbin/init \
  systemd.setenv=INTFTYPE=eth \
  systemd.setenv=ETBA=1 \
  systemd.setenv=SKIP_ZEROTOUCH_BARRIER_IN_SYSDBINIT=1 \
  systemd.setenv=CEOS=1 \
  systemd.setenv=EOS_PLATFORM=ceoslab \
  systemd.setenv=container=docker \
  systemd.setenv=MAPETH0=1 \
  systemd.setenv=MGMT_INTF=eth0 >/dev/null

#  -p 2022:22 \
#  -p 8443:443 \
#  -p 8080:80 \

docker start "$CEOS_CONTAINER" >/dev/null

echo "Waiting for cEOS to initialize..."
docker logs -f "$CEOS_CONTAINER" | grep -q "SYS-5-SYSTEM_INITIALIZED"

mgmt_ip_addr=$(docker inspect "$CEOS_CONTAINER" -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}/{{.IPPrefixLen}}{{end}}')
mgmt_gateway=$(docker inspect "$CEOS_CONTAINER" -f '{{range .NetworkSettings.Networks}}{{.Gateway}}{{end}}')

docker exec -i "$CEOS_CONTAINER" Cli -p 15 <<EOF
configure
hostname ceoslab
username admin privilege 15 nopassword
aaa authorization exec default local
aaa authentication policy local allow-nopassword-remote-login
interface Management0
  ip address $mgmt_ip_addr
management api gnmi
  transport grpc DEFAULT
    no shutdown
ip route 0.0.0.0/0 $mgmt_gateway
end
EOF

echo "Container is up. Run 'docker exec -it $CEOS_CONTAINER Cli -p 15' to connect."
