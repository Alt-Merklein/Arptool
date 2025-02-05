IFACE=$(cat ./config.yaml | yq .network.sniff_iface | tr -d '"')

echo "Disabling promiscuous mode on $IFACE"
sudo ifconfig "$IFACE" -promisc   