for NAMESPACE in "${NAMESPACES[@]}"; do
  echo "Deleting namespace: $NAMESPACE"
  kubectl delete namespace $NAMESPACE
done
