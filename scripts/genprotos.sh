#!/usr/bin/env bash
# echo "Updating gNMI amd gRPC sub-modules..."
# git submodule add https://github.com/openconfig/gnmi.git submodule/openconfig
# git submodule add https://github.com/grpc/grpc.git submodule/grpc
# git submodule update --remote
# SUBMODULE_DIR=submodule

#set -x
set -e

WORKDIR=$(mktemp -d)
trap 'test -d "$WORKDIR" && rm -rf "$WORKDIR"' EXIT

# Downloading protos
wget https://raw.githubusercontent.com/openconfig/gnmi/master/proto/gnmi/gnmi.proto -O "$WORKDIR/gnmi.proto"
wget https://raw.githubusercontent.com/openconfig/gnmi/master/proto/gnmi_ext/gnmi_ext.proto -O "$WORKDIR/gnmi_ext.proto"
wget https://raw.githubusercontent.com/grpc/grpc/master/src/proto/grpc/status/status.proto -O "$WORKDIR/status.proto"
wget https://raw.githubusercontent.com/openconfig/gnmi/master/proto/target/target.proto -O "$WORKDIR/target.proto"

echo "Fixing proto imports..."
case $OSTYPE in
  "darwin"*)
    sed -i '' 's/github.com\/openconfig\/gnmi\/proto\/gnmi_ext\///g' "$WORKDIR/gnmi.proto"
    sed -i '' 's/github.com\/openconfig\/gnmi\/proto\/gnmi_ext\///g' "$WORKDIR/gnmi.proto"
    sed -i '' 's/github.com\/openconfig\/gnmi\/proto\/gnmi\///g' "$WORKDIR/target.proto"
    ;;
  *)
    sed -i 's/github.com\/openconfig\/gnmi\/proto\/gnmi_ext\///g' "$WORKDIR/gnmi.proto"
    sed -i 's/github.com\/openconfig\/gnmi\/proto\/gnmi_ext\///g' "$WORKDIR/gnmi.proto"
    sed -i 's/github.com\/openconfig\/gnmi\/proto\/gnmi\///g' "$WORKDIR/target.proto"
    ;;
esac

echo "Generating python modules..."
python3 -m grpc_tools.protoc \
  --proto_path="$WORKDIR" \
  --python_out="$WORKDIR" \
  --grpc_python_out="$WORKDIR" \
  --pyi_out="$WORKDIR" \
  "$WORKDIR/gnmi.proto" "$WORKDIR/gnmi_ext.proto" "$WORKDIR/status.proto" "$WORKDIR/target.proto"
  # --mypy_out="$WORKDIR" \

echo "Fixing python imports..."
case $OSTYPE in
  "darwin"*)
    sed -i '' 's/import gnmi_pb2/from . import gnmi_pb2/' "$WORKDIR/gnmi_pb2_grpc.py"
    #sed -i '' 's/import gnmi_pb2/from . import gnmi_pb2/' "$WORKDIR/gnmi_pb2_grpc.pyi"
    sed -i '' 's/import gnmi_ext_pb2/from . import gnmi_ext_pb2/' "$WORKDIR/gnmi_pb2.py"
    sed -i '' 's/import gnmi_ext_pb2/from . import gnmi_ext_pb2/' "$WORKDIR/gnmi_pb2.pyi"
    sed -i '' 's/import gnmi_pb2/from . import gnmi_pb2/' "$WORKDIR/target_pb2.py"
    ;;
  *)
    sed -i 's/import gnmi_pb2/from . import gnmi_pb2/' "$WORKDIR/gnmi_pb2_grpc.py"
    #sed -i 's/import gnmi_pb2/from . import gnmi_pb2/' "$WORKDIR/gnmi_pb2_grpc.pyi"
    sed -i 's/import gnmi_ext_pb2/from . import gnmi_ext_pb2/' "$WORKDIR/gnmi_pb2.py"
    sed -i 's/import gnmi_ext_pb2/from . import gnmi_ext_pb2/' "$WORKDIR/gnmi_pb2.pyi"
    sed -i 's/import gnmi_pb2/from . import gnmi_pb2/' "$WORKDIR/target_pb2.py"
    ;;
esac

echo "Copying modules to project..."
cp -p "$WORKDIR"/*.py* gnmi/proto/
