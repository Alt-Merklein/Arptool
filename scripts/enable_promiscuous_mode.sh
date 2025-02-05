IFACE=$(cat ./config.yaml | yq .network.sniff_iface | tr -d '"')

echo "Enabling promiscuous mode on $IFACE"
sudo ifconfig $IFACE promisc   