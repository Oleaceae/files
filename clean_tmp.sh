for i in $(seq 0 5); do
    ssh node-$i "sudo rm -rf /tmp/*"
    echo "node-$i done"
done
